# Bands

> An opinionated framework for getting shit done with a band of AI agents.

**Bands** scaffolds and runs a small "band" of AI agents on top of a headless
agent harness ([Claude Code](https://claude.com/claude-code) by default). You
define a roster of agents — each with a role, an operating mode, and a workspace — and Bands lays down a `.bands/`
directory that gives them durable memory, an inbox to talk to each other, rooms
to meet in, and shell scripts that wake them on a "heartbeat" to do work.

It's vendor-agnostic plumbing: shell scripts that run headless agent sessions
through a pluggable harness adapter, plus a read-only dashboard to watch what
your agents are up to.

## Backstory

Bands is the generalized, cleaned-up successor to a private experiment called
*Office* — an AI C-suite that acted as advisors, and occasionally actors, for my consultancy. 

That story (what worked, what very much did not, and why **scope is the whole game**) is told in the blog
post **"I Created An Agentic Advisory Board And They Mostly Just Annoyed Me."**
This repo is the reusable skeleton extracted from it.

## Quick start

Bands is a Python package managed with [uv](https://docs.astral.sh/uv/).

```bash
# Install as a tool (from source)
uv tool install git+https://github.com/manbradcalf/bands
# ...or run without installing
uvx --from git+https://github.com/manbradcalf/bands bands --help

# Scaffold a band into the current repo (interactive)
bands init

# Watch your agents in the dashboard
bands dashboard
```

Developing locally:

```bash
git clone https://github.com/manbradcalf/bands
cd bands
uv sync
uv run bands --help
```

## What `bands init` creates

`bands init` asks for a band name, a GitHub repo/project for task tracking, a
roster of employees, and any initial sprints, then writes a `.bands/` workspace:

```
.bands/
├── bands.json              # your band's config (roster, GitHub, sprints)
├── PURPOSE.md              # why this band exists
├── IDENTITY.md             # what the agents are (probabilistic, session-based)
├── EXPECTATIONS.md         # honesty / grounding / scope discipline
├── HEURISTICS.md           # decision-making rules
├── OPERATING_MODES.md      # advisory / operational / execution
├── CLAUDE.md               # workspace overview the agents read first
├── suites/                 # one folder per employee
│   └── <slug>/             #   CLAUDE.md, HEARTBEAT.md, directives, inbox/, work/
├── commons/                # shared state: ceo-directives, sprint/, roundtables/,
│   │                       #   summaries/, activity.md, mail-log.json
│   └── sprint/NORTH_STAR.md
├── boardroom/              # C-suite meeting minutes + inbox
├── lobby/  breakroom/      # inbound info / informal exchanges
└── bin/                    # beat.sh, band-beat.sh, roundtable.sh,
                            #   config.sh, adapters/ (claude.sh, pi.sh)
```

### Operating modes

Each agent runs in one of three modes:

- **Advisory** — strategy; challenges assumptions, doesn't own execution.
- **Operational** — owns a domain and executes within it.
- **Execution** — follows a playbook and flags exceptions.

### The heartbeat

Agents don't run continuously — they wake on a *heartbeat*. `.bands/bin/band-beat.sh`
runs a full cycle (a quick roundtable to sync, then individual deep work, then a
commit), `beat.sh` wakes a single employee, and `roundtable.sh` runs a fast
multi-round discussion. Wire these to cron for autonomy, or run them by hand.

### Choosing the harness

The scripts never call an agent CLI directly. They call `agent_run work` (deep
work) or `agent_run roundtable` (quick chat), and the adapter named in
`bands.json` turns that into a real command. The default:

```json
"harness": {
  "adapter": "claude",
  "models": { "work": "sonnet", "roundtable": "haiku" }
}
```

Bands ships `claude` (Claude Code) and `pi` adapters. To switch, change
`adapter` and the two model IDs. To override for one run:

```bash
BANDS_ADAPTER=pi BANDS_WORK_MODEL=<model> BANDS_ROUNDTABLE_MODEL=<model> .bands/bin/band-beat.sh
```

To add another harness, see `.bands/bin/adapters/README.md`.

## The dashboard

`bands dashboard` serves a read-only view of a `.bands/` workspace — the floor
plan of agents and rooms, each agent's inbox and work, room minutes, the
activity feed, and (optionally) their GitHub tasks.

```bash
bands dashboard --dir .            # serve the band in the current repo
bands dashboard --dir examples/demo-band   # try it against the bundled demo
```

There's a fully fictional **demo band** under `examples/demo-band/` so you can
see the dashboard with real content before scaffolding your own.

## Requirements

- **Python ≥ 3.11** and **uv**.
- An **agent harness** to run the heartbeat scripts: **Claude Code** (`claude`
  CLI) by default, or [pi](https://github.com/earendil-works/pi) (`pi` CLI).
- **GitHub CLI** (`gh`) — *optional*. Tasks are GitHub issues; if `gh` isn't
  installed or authenticated, the dashboard's task panels simply show a
  "not configured" state.

## License

[MIT](./LICENSE)
