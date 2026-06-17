"""Flask app factory for the read-only Bands dashboard."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, render_template

from bands.dashboard import gh, workspace


def create_app(bands_root: Path) -> Flask:
    """Build the dashboard app for a given `.bands/` workspace directory."""
    bands_root = Path(bands_root)
    app = Flask(__name__)
    app.config["BANDS_ROOT"] = bands_root

    @app.context_processor
    def inject_band():
        config = workspace.load_config(bands_root)
        return {"band_name": config.get("name") or "Bands"}

    # --- Index ---
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            employees=workspace.get_employees(bands_root),
            rooms=workspace.get_rooms(bands_root),
        )

    # --- Suites ---
    @app.route("/suite/<slug>")
    def suite(slug: str):
        emp = workspace.get_employee(bands_root, slug)
        if emp is None:
            abort(404)
        content = workspace.read_claude_md(bands_root / "suites" / slug)
        return render_template(
            "suite.html",
            emp=emp,
            tab="overview",
            content_html=workspace.md_to_html(content) if content else None,
        )

    @app.route("/suite/<slug>/inbox")
    def suite_inbox(slug: str):
        emp = workspace.get_employee(bands_root, slug)
        if emp is None:
            abort(404)
        return render_template(
            "inbox.html",
            emp=emp,
            tab="inbox",
            messages=workspace.get_inbox_messages(bands_root, slug),
            read_messages=workspace.get_read_messages(bands_root, slug),
        )

    @app.route("/suite/<slug>/work")
    def suite_work(slug: str):
        emp = workspace.get_employee(bands_root, slug)
        if emp is None:
            abort(404)
        return render_template(
            "work.html",
            emp=emp,
            tab="work",
            items=workspace.get_work_items(bands_root, slug),
        )

    @app.route("/suite/<slug>/tasks")
    def suite_tasks(slug: str):
        emp = workspace.get_employee(bands_root, slug)
        if emp is None:
            abort(404)
        config = workspace.load_config(bands_root)
        result = gh.get_items_by_label(config, emp["label"])
        return render_template(
            "tasks.html",
            emp=emp,
            tab="tasks",
            result=result,
        )

    # --- Rooms ---
    @app.route("/room/<slug>")
    def room(slug: str):
        data = workspace.get_room(bands_root, slug)
        if data is None:
            abort(404)
        return render_template("room.html", room=data)

    @app.route("/room/<room_slug>/minutes/<minutes_slug>")
    def minutes(room_slug: str, minutes_slug: str):
        html = workspace.get_minutes(bands_root, room_slug, minutes_slug)
        if html is None:
            abort(404)
        return render_template(
            "minutes.html",
            room_slug=room_slug,
            room_name=room_slug.replace("-", " ").title(),
            minutes_name=minutes_slug,
            content_html=html,
        )

    # --- Pulse (activity + mail) ---
    @app.route("/pulse")
    def pulse():
        return render_template(
            "pulse.html",
            entries=workspace.parse_activity_entries(bands_root),
            mail_log=workspace.load_mail_log(bands_root),
            employees=workspace.get_employees(bands_root),
        )

    return app
