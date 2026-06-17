"""GitHub task integration via the `gh` CLI.

Tasks live as GitHub issues; each employee owns the issues carrying their label
(from bands.json). Every call degrades gracefully: if `gh` is missing, not
authenticated, or errors, we return an "unavailable" result instead of raising,
so the dashboard renders a "not configured" panel rather than a 500.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time

_cache: dict = {}
CACHE_TTL = 30

UNAVAILABLE_MSG = (
    "GitHub tasks are not configured. Install the `gh` CLI and run `gh auth login`, "
    "and set gh_owner/gh_repo in .bands/bands.json."
)


def _repo(config: dict) -> str | None:
    owner = config.get("gh_owner")
    repo = config.get("gh_repo")
    if owner and repo:
        return f"{owner}/{repo}"
    return None


def _fetch_issues(repo: str) -> dict:
    """Return {"available": bool, "items": [...], "error": str|None}."""
    if not shutil.which("gh"):
        return {"available": False, "items": [], "error": UNAVAILABLE_MSG}
    cmd = [
        "gh", "issue", "list",
        "--repo", repo,
        "--state", "open",
        "--json", "number,title,url,labels",
        "--limit", "100",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception as exc:  # noqa: BLE001 - graceful degradation
        return {"available": False, "items": [], "error": str(exc)}
    if result.returncode != 0:
        return {
            "available": False,
            "items": [],
            "error": result.stderr.strip() or UNAVAILABLE_MSG,
        }
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"available": False, "items": [], "error": "Bad gh output"}
    items = [
        {
            "number": i["number"],
            "title": i["title"],
            "url": i.get("url", ""),
            "labels": [l["name"] for l in i.get("labels", [])],
        }
        for i in raw
    ]
    return {"available": True, "items": items, "error": None}


def get_all_items(config: dict) -> dict:
    repo = _repo(config)
    if not repo:
        return {"available": False, "items": [], "error": UNAVAILABLE_MSG}
    now = time.time()
    if repo in _cache and now - _cache[repo][0] < CACHE_TTL:
        return _cache[repo][1]
    result = _fetch_issues(repo)
    _cache[repo] = (now, result)
    return result


def get_items_by_label(config: dict, label: str) -> dict:
    result = get_all_items(config)
    if not result["available"]:
        return result
    label = (label or "").lower()
    items = [
        item for item in result["items"]
        if label in [l.lower() for l in item.get("labels", [])]
    ]
    return {"available": True, "items": items, "error": None}
