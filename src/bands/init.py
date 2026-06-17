"""Interactive band initialization."""

import json
from pathlib import Path

import click

from bands.scaffold import scaffold_band


def prompt_employees() -> list[dict]:
    """Prompt for employee definitions."""
    employees = []
    click.echo("\n--- Employees ---")
    click.echo("Define your team. Each employee gets a name, role, and operating mode.")
    click.echo("Operating modes: advisory (strategy), operational (execution owner), execution (follows playbook)")
    click.echo()

    while True:
        name = click.prompt("Employee name (or 'done')", default="done")
        if name.lower() == "done":
            if not employees:
                click.echo("You need at least one employee.")
                continue
            break

        role = click.prompt("  Role (e.g. CTO, CMO, SDR)")
        slug = click.prompt("  Suite slug", default=f"{name.lower()}-{role.lower()}")
        mode = click.prompt(
            "  Operating mode",
            type=click.Choice(["advisory", "operational", "execution"]),
            default="operational",
        )
        label = click.prompt("  GH issue label", default=role.lower())

        employees.append({
            "name": name,
            "role": role,
            "slug": slug,
            "mode": mode,
            "label": label,
        })
        click.echo(f"  Added {name} ({role})\n")

    return employees


def prompt_sprints() -> list[dict]:
    """Prompt for initial sprint/north star definitions."""
    sprints = []
    click.echo("\n--- Sprints ---")
    click.echo("Define north star goals your band will work toward.")
    click.echo("Each sprint is a series of heartbeats focused on a goal.\n")

    while True:
        name = click.prompt("Sprint name (or 'done')", default="done")
        if name.lower() == "done":
            break

        goal = click.prompt("  North star goal (one sentence)")
        heartbeats = click.prompt("  Heartbeat count", type=int, default=10)

        sprints.append({
            "name": name,
            "goal": goal,
            "heartbeats": heartbeats,
        })
        click.echo(f"  Added sprint: {name} ({heartbeats} heartbeats)\n")

    return sprints


def init_band(target_dir: str):
    """Run the interactive init flow."""
    target = Path(target_dir).resolve()
    click.echo(f"Initializing a new band in {target}\n")

    # 1. Band name
    band_name = click.prompt("Band name", default=target.name)

    # 2. GitHub project
    click.echo("\n--- GitHub Integration ---")
    gh_owner = click.prompt("GH repo owner")
    gh_repo = click.prompt("GH repo name", default=band_name)
    gh_project = click.prompt("GH project number (for task board)", type=int)

    # 3. Employees
    employees = prompt_employees()

    # 4. Sprints
    sprints = prompt_sprints()

    # 5. Confirm
    click.echo("\n--- Summary ---")
    click.echo(f"Band: {band_name}")
    click.echo(f"Repo: {gh_owner}/{gh_repo}")
    click.echo(f"Project: #{gh_project}")
    click.echo(f"Employees: {', '.join(e['name'] + ' (' + e['role'] + ')' for e in employees)}")
    if sprints:
        click.echo(f"Sprints: {', '.join(s['name'] for s in sprints)}")
    else:
        click.echo("Sprints: none yet")
    click.echo()

    if not click.confirm("Scaffold this band?", default=True):
        click.echo("Aborted.")
        return

    # 6. Build it
    config = {
        "name": band_name,
        "gh_owner": gh_owner,
        "gh_repo": gh_repo,
        "gh_project": gh_project,
        "employees": employees,
        "sprints": sprints,
    }

    scaffold_band(target, config)
    click.echo(f"\nBand scaffolded at {target / '.bands'}")
    click.echo("Next: review .bands/, then run .bands/bin/band-beat.sh")
