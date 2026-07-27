"""Interactive band initialization."""

import json
import subprocess
from pathlib import Path

import click

from bands.scaffold import scaffold_band


def create_gh_project(owner: str, title: str) -> int:
    """Create a new GitHub project and return its number."""
    result = subprocess.run(
        [
            "gh", "project", "create",
            "--owner", owner,
            "--title", title,
            "--format", "json",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(
            f"Failed to create GitHub project: {result.stderr.strip()}"
        )
    data = json.loads(result.stdout)
    return int(data["number"])


def ensure_gh_repo(owner: str, repo: str) -> None:
    """Make sure the task-tracking repo exists; offer to create it if not."""
    check = subprocess.run(
        ["gh", "repo", "view", f"{owner}/{repo}"],
        capture_output=True,
    )
    if check.returncode == 0:
        return

    click.echo(f"  GitHub repo {owner}/{repo} does not exist.")
    if not click.confirm("  Create it?", default=True):
        raise click.ClickException(
            f"Repo {owner}/{repo} is required for issue tracking. "
            "Create it and re-run `bands init`."
        )
    visibility = click.prompt(
        "  Visibility", type=click.Choice(["private", "public"]), default="private"
    )
    result = subprocess.run(
        ["gh", "repo", "create", f"{owner}/{repo}", f"--{visibility}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(
            f"Failed to create GitHub repo: {result.stderr.strip()}"
        )
    click.echo(f"  Created {owner}/{repo} ({visibility})")


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
    ensure_gh_repo(gh_owner, gh_repo)
    if click.confirm("Create a new GitHub project for this band?", default=True):
        gh_project = create_gh_project(gh_owner, band_name)
        click.echo(f"  Created GH project #{gh_project}")
    else:
        gh_project = click.prompt("GH project number (for task board)", type=int)

    # 3. Engine (agent harness)
    from bands.engines import engine_names
    engine = click.prompt(
        "\nAgent engine (harness that runs your agents)",
        default="claude",
        type=click.Choice(engine_names()),
    )

    # 4. Employees
    employees = prompt_employees()

    # 5. Sprints
    sprints = prompt_sprints()

    # 6. Confirm
    click.echo("\n--- Summary ---")
    click.echo(f"Band: {band_name}")
    click.echo(f"Engine: {engine}")
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

    # 7. Build it
    config = {
        "name": band_name,
        "engine": {"default": engine},
        "gh_owner": gh_owner,
        "gh_repo": gh_repo,
        "gh_project": gh_project,
        "employees": employees,
        "sprints": sprints,
    }

    scaffold_band(target, config)
    click.echo(f"\nBand scaffolded at {target / '.bands'}")
    click.echo("Next: review .bands/, then run .bands/bin/band-beat.sh")
