"""Run one agent heartbeat through the configured engine.

The bin/*.sh scripts in a .bands/ workspace call this instead of invoking
`claude` (or any harness) directly. Engine and model selection come from
bands.json:

    {
      "engine": {
        "default": "claude",                  // or "pi"
        "models": {                           // optional per-engine tier map
          "claude": { "smart": "sonnet", "fast": "haiku" },
          "pi":     { "smart": "openrouter/anthropic/claude-sonnet-4.5" }
        }
      },
      "employees": [
        { "slug": "maria-cto", "engine": "pi", ... }   // optional per-agent override
      ]
    }

Backwards compatible: no "engine" block means Claude Code with the historical
sonnet/haiku defaults.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from bands.engines import get_engine

DEFAULT_ENGINE = "claude"
TIERS = ("smart", "fast")


@dataclass
class ResolvedAgent:
    engine_name: str
    model: str | None
    argv: list[str]
    cwd: Path


def load_config(bands_dir: Path) -> dict:
    cfg_path = bands_dir / "bands.json"
    with open(cfg_path) as f:
        return json.load(f)


def resolve(
    bands_dir: Path,
    suite: str,
    tier: str,
    prompt: str,
    allowed_tools: str | None,
) -> ResolvedAgent:
    if tier not in TIERS:
        raise ValueError(f"tier must be one of {TIERS}, got {tier!r}")

    config = load_config(bands_dir)
    engine_cfg = config.get("engine", {})
    engine_name = engine_cfg.get("default", DEFAULT_ENGINE)

    # Per-employee override.
    for emp in config.get("employees", []):
        if emp.get("slug") == suite and emp.get("engine"):
            engine_name = emp["engine"]
            break

    engine = get_engine(engine_name)

    # Model: bands.json per-engine tier map → engine built-in default → None
    # (None = harness picks its own default model).
    model = engine_cfg.get("models", {}).get(engine_name, {}).get(tier)
    if model is None:
        model = engine.default_models.get(tier)

    if shutil.which(engine.binary) is None:
        raise RuntimeError(
            f"engine {engine_name!r} requires `{engine.binary}` on PATH but it was not found"
        )

    cwd = bands_dir / "suites" / suite
    if not cwd.is_dir():
        raise RuntimeError(f"suite not found: {cwd}")

    return ResolvedAgent(
        engine_name=engine_name,
        model=model,
        argv=engine.command(prompt, model, cwd, allowed_tools),
        cwd=cwd,
    )


def run(
    bands_dir: Path,
    suite: str,
    tier: str,
    prompt: str,
    allowed_tools: str | None = None,
) -> int:
    agent = resolve(bands_dir, suite, tier, prompt, allowed_tools)
    model_note = agent.model or "(engine default)"
    print(f"[bands] engine={agent.engine_name} model={model_note} suite={suite}", file=sys.stderr)
    proc = subprocess.run(agent.argv, cwd=agent.cwd)
    return proc.returncode
