"""Scaffold a band from config."""

import json
from pathlib import Path

from jinja2 import Environment, PackageLoader


def get_templates() -> Environment:
    return Environment(
        loader=PackageLoader("bands", "templates"),
        keep_trailing_newline=True,
    )


def scaffold_band(target: Path, config: dict):
    """Create the full band directory structure inside .bands/ of the target repo."""
    env = get_templates()
    bands_dir = target / ".bands"
    bands_dir.mkdir(parents=True, exist_ok=True)

    # Config file
    (bands_dir / "bands.json").write_text(json.dumps(config, indent=2) + "\n")

    # Foundational docs
    for doc in ["PURPOSE", "IDENTITY", "EXPECTATIONS", "HEURISTICS", "OPERATING_MODES"]:
        tmpl = env.get_template(f"{doc}.md")
        (bands_dir / f"{doc}.md").write_text(tmpl.render(**config))

    # Band CLAUDE.md (inside .bands/)
    tmpl = env.get_template("CLAUDE.md")
    (bands_dir / "CLAUDE.md").write_text(tmpl.render(**config))

    # Root CLAUDE.md pointer (in repo root, only if not already present)
    root_claude = target / "CLAUDE.md"
    pointer = "# Bands\n\nThis repo has an AI agent band. See [.bands/CLAUDE.md](.bands/CLAUDE.md) for the full setup.\n"
    if root_claude.exists():
        existing = root_claude.read_text()
        if ".bands/" not in existing:
            with open(root_claude, "a") as f:
                f.write(f"\n{pointer}")
    else:
        root_claude.write_text(pointer)

    # Rooms
    for room in ["boardroom", "commons", "lobby", "breakroom"]:
        room_dir = bands_dir / room
        room_dir.mkdir(exist_ok=True)
        if room == "boardroom":
            (room_dir / "minutes").mkdir(exist_ok=True)
            (room_dir / "inbox").mkdir(exist_ok=True)
            (room_dir / "inbox" / "read").mkdir(exist_ok=True)
        if room == "commons":
            (room_dir / "roundtables").mkdir(exist_ok=True)
            (room_dir / "summaries").mkdir(exist_ok=True)

    # Directives
    commons = bands_dir / "commons"
    tmpl = env.get_template("ceo-directives.md")
    (commons / "ceo-directives.md").write_text(tmpl.render(**config))

    # Sprint dirs
    sprint_dir = commons / "sprint"
    sprint_dir.mkdir(exist_ok=True)
    (sprint_dir / "roundtables").mkdir(exist_ok=True)
    (commons / "sprints-archive").mkdir(exist_ok=True)

    # Write north stars for any initial sprints
    for sprint in config.get("sprints", []):
        tmpl = env.get_template("NORTH_STAR.md")
        (sprint_dir / "NORTH_STAR.md").write_text(tmpl.render(sprint=sprint))

    # Employee suites
    suites = bands_dir / "suites"
    suites.mkdir(exist_ok=True)

    for emp in config["employees"]:
        suite = suites / emp["slug"]
        suite.mkdir(exist_ok=True)
        (suite / "inbox").mkdir(exist_ok=True)
        (suite / "inbox" / "read").mkdir(exist_ok=True)
        (suite / "work").mkdir(exist_ok=True)

        ctx = {**config, "employee": emp}

        for tmpl_name, out_name in [
            ("employee-CLAUDE.md", "CLAUDE.md"),
            ("employee-HEARTBEAT.md", "HEARTBEAT.md"),
            ("employee-directives.md", f"{emp['slug']}-directives.md"),
            ("employee-AGENTS.md", "AGENTS.md"),
        ]:
            tmpl = env.get_template(tmpl_name)
            (suite / out_name).write_text(tmpl.render(**ctx))

    # Bin scripts
    bin_dir = bands_dir / "bin"
    bin_dir.mkdir(exist_ok=True)

    for script in ["beat.sh", "band-beat.sh", "roundtable.sh"]:
        tmpl = env.get_template(f"bin/{script}")
        path = bin_dir / script
        path.write_text(tmpl.render(**config))
        path.chmod(0o755)

    # Mail log
    (commons / "mail-log.json").write_text("[]\n")
