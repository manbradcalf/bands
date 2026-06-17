"""Read the .bands/ workspace tree for the dashboard.

Everything here is read-only. The dashboard is an observability window onto the
artifacts the agents themselves write: suite docs, inboxes, work, room minutes,
the activity feed, and the mail log. No external database — the repo is the memory.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import markdown

# Role badge palette — keyed by employee order, so any role name gets a colour
# without hardcoding cto/cmo/etc.
PALETTE = [
    ("#1e3a5f", "#7eb8da"),
    ("#3a1e5f", "#b87eda"),
    ("#1e5f3a", "#7edab8"),
    ("#5f3a1e", "#dab87e"),
    ("#5f1e1e", "#da7e7e"),
    ("#5f5f1e", "#dada7e"),
    ("#1e5f5f", "#7edada"),
    ("#3a3a5f", "#9e9eda"),
]

# Top-level entries under .bands/ that are not "rooms".
_NON_ROOMS = {"suites", "bin"}


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split simple `key: value` YAML-ish frontmatter from a markdown body."""
    meta: dict = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ": " in line:
                    key, val = line.split(": ", 1)
                    meta[key.strip()] = val.strip()
            body = parts[2].strip()
    return meta, body


def load_config(bands_root: Path) -> dict:
    cfg_path = bands_root / "bands.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text())
        except Exception:
            return {}
    return {}


def read_claude_md(path: Path) -> str | None:
    md_path = path / "CLAUDE.md"
    if md_path.exists():
        return md_path.read_text()
    return None


def _inbox_counts(suite_dir: Path) -> dict:
    inbox_dir = suite_dir / "inbox"
    unread = 0
    must_read = 0
    if inbox_dir.exists():
        for md_file in inbox_dir.glob("*.md"):
            unread += 1
            meta, _ = parse_frontmatter(md_file.read_text())
            if "must-read" in meta.get("priority", ""):
                must_read += 1
    return {"unread": unread, "must_read": must_read}


def get_employees(bands_root: Path) -> list[dict]:
    """Employee roster, driven by bands.json (not by parsing slug strings)."""
    config = load_config(bands_root)
    suites_dir = bands_root / "suites"
    employees = []
    for i, emp in enumerate(config.get("employees", [])):
        slug = emp.get("slug", "")
        suite_dir = suites_dir / slug
        bg, fg = PALETTE[i % len(PALETTE)]
        counts = _inbox_counts(suite_dir)
        employees.append({
            "slug": slug,
            "name": emp.get("name", slug),
            "role": emp.get("role", ""),
            "mode": emp.get("mode", ""),
            "label": emp.get("label", ""),
            "color_bg": bg,
            "color_fg": fg,
            "has_content": read_claude_md(suite_dir) is not None,
            "unread_count": counts["unread"],
            "must_read_count": counts["must_read"],
        })
    return employees


def get_employee(bands_root: Path, slug: str) -> dict | None:
    for emp in get_employees(bands_root):
        if emp["slug"] == slug:
            return emp
    return None


def get_rooms(bands_root: Path) -> list[dict]:
    rooms = []
    for item in sorted(bands_root.iterdir()):
        if not item.is_dir() or item.name in _NON_ROOMS or item.name.startswith("."):
            continue
        minutes_dir = item / "minutes"
        minutes = []
        if minutes_dir.exists():
            minutes = sorted((f.stem for f in minutes_dir.glob("*.md")), reverse=True)
        rooms.append({
            "slug": item.name,
            "name": item.name.replace("-", " ").title(),
            "has_content": read_claude_md(item) is not None,
            "has_minutes": minutes_dir.exists(),
            "minutes": minutes,
        })
    return rooms


def _read_messages(message_dir: Path) -> list[dict]:
    messages = []
    if not message_dir.exists():
        return messages
    for md_file in sorted(message_dir.glob("*.md"), reverse=True):
        meta, body = parse_frontmatter(md_file.read_text())
        messages.append({
            "filename": md_file.name,
            "from": meta.get("from", "Unknown"),
            "from_slug": meta.get("from_slug") or None,
            "to": meta.get("to", ""),
            "date": meta.get("date", ""),
            "subject": meta.get("subject", md_file.stem),
            "priority": meta.get("priority", ""),
            "body_html": md_to_html(body),
        })
    return messages


def get_inbox_messages(bands_root: Path, slug: str) -> list[dict]:
    return _read_messages(bands_root / "suites" / slug / "inbox")


def get_read_messages(bands_root: Path, slug: str) -> list[dict]:
    return _read_messages(bands_root / "suites" / slug / "inbox" / "read")


def get_work_items(bands_root: Path, slug: str) -> list[dict]:
    work_dir = bands_root / "suites" / slug / "work"
    items = []
    if not work_dir.exists():
        return items
    for f in sorted(work_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = f.stem.replace("-", " ").title()
        for line in text.splitlines():
            if line.strip().startswith("#"):
                title = line.strip().lstrip("#").strip()
                break
        items.append({
            "filename": f.name,
            "title": title,
            "modified": f.stat().st_mtime,
            "html": md_to_html(text),
        })
    items.sort(key=lambda x: x["modified"], reverse=True)
    return items


def get_room(bands_root: Path, slug: str) -> dict | None:
    room_path = bands_root / slug
    if slug in _NON_ROOMS or not room_path.is_dir() or slug.startswith("."):
        return None
    minutes_dir = room_path / "minutes"
    minutes = []
    if minutes_dir.exists():
        minutes = sorted(
            ({"name": f.stem, "slug": f.stem} for f in minutes_dir.glob("*.md")),
            key=lambda m: m["name"],
            reverse=True,
        )
    # Other markdown files directly in the room (e.g. ceo-directives.md, activity.md)
    files = [
        {"name": f.stem, "filename": f.name}
        for f in sorted(room_path.glob("*.md"))
        if f.name != "CLAUDE.md"
    ]
    content = read_claude_md(room_path)
    return {
        "slug": slug,
        "name": slug.replace("-", " ").title(),
        "content_html": md_to_html(content) if content else None,
        "minutes": minutes,
        "has_minutes": minutes_dir.exists(),
        "files": files,
    }


def get_minutes(bands_root: Path, room_slug: str, minutes_slug: str) -> str | None:
    path = bands_root / room_slug / "minutes" / f"{minutes_slug}.md"
    if not path.exists():
        return None
    return md_to_html(path.read_text())


def parse_activity_entries(bands_root: Path) -> list[dict]:
    """Parse commons/activity.md into individual entries (## Who — When)."""
    activity_path = bands_root / "commons" / "activity.md"
    if not activity_path.exists():
        return []
    content = activity_path.read_text()
    entries = []
    for section in re.split(r"\n---\n", content):
        section = section.strip()
        if not section or section.startswith("# "):
            continue
        h2 = re.match(r"## (.+?) — (.+)", section)
        if h2:
            entries.append({
                "who": h2.group(1).strip(),
                "when": h2.group(2).strip(),
                "body_html": md_to_html(section),
            })
    return entries


def load_mail_log(bands_root: Path) -> list:
    mail_log = bands_root / "commons" / "mail-log.json"
    if mail_log.exists():
        try:
            return json.loads(mail_log.read_text())
        except Exception:
            return []
    return []
