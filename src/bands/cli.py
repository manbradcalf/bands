"""Bands CLI — scaffold and manage AI agent teams."""

from pathlib import Path

import click

from bands.init import init_band
from bands.run import run as run_agent


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
@click.option("--dir", "bands_dir", required=True, type=click.Path(exists=True, file_okay=False),
              help="Path to the .bands/ workspace directory")
@click.option("--suite", required=True, help="Employee suite slug")
@click.option("--tier", default="smart", show_default=True, type=click.Choice(["smart", "fast"]),
              help="Model tier (mapped per engine in bands.json)")
@click.option("--allowed-tools", default=None, help="Tool allowlist passed through to the engine")
@click.argument("prompt")
def run(bands_dir: str, suite: str, tier: str, allowed_tools: str | None, prompt: str):
    """Run one agent heartbeat through the configured engine (claude, pi, ...)."""
    raise SystemExit(run_agent(Path(bands_dir), suite, tier, prompt, allowed_tools))


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
