"""Bands CLI — scaffold and manage AI agent teams."""

from pathlib import Path

import click

from bands.init import init_band


@click.group()
def main():
    """Bands — get shit done with a team of AI agents."""
    pass


@main.command()
@click.option("--dir", "target_dir", default=".", help="Directory to scaffold into")
def init(target_dir: str):
    """Initialize a new band interactively."""
    init_band(target_dir)


@main.command()
@click.option("--dir", "target_dir", default=".", help="Repo containing a .bands/ workspace")
@click.option("--port", default=5001, show_default=True, help="Port to serve on")
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind")
def dashboard(target_dir: str, port: int, host: str):
    """Launch the read-only dashboard for a .bands/ workspace."""
    bands_root = (Path(target_dir).resolve()) / ".bands"
    if not bands_root.is_dir():
        raise click.ClickException(
            f"No .bands/ workspace found in {Path(target_dir).resolve()}. "
            "Run `bands init` first, or pass --dir to point at a band."
        )

    from bands.dashboard.app import create_app

    app = create_app(bands_root)
    click.echo(f"Serving {bands_root} at http://{host}:{port}")
    app.run(host=host, port=port)
