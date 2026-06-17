"""Bands CLI — scaffold and manage AI agent teams."""

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
