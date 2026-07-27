"""Engine abstraction: how bands invokes a headless coding agent.

An Engine knows how to turn (prompt, model, cwd) into a shell command for a
specific agent harness (Claude Code, pi, ...). Everything else in bands —
suites, inboxes, heartbeats, the dashboard — is plain files and therefore
engine-agnostic.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EngineSpec:
    """Describes one agent harness."""

    name: str
    # Binary required on PATH.
    binary: str
    # Default models per tier when bands.json doesn't specify them.
    # None = let the harness use its own configured default.
    default_models: dict[str, str | None] = field(default_factory=dict)

    def command(
        self,
        prompt: str,
        model: str | None,
        cwd: Path,
        allowed_tools: str | None,
    ) -> list[str]:
        """Build the argv for one non-interactive agent invocation."""
        raise NotImplementedError


class UnknownEngineError(Exception):
    pass
