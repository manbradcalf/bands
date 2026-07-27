"""Claude Code engine (https://claude.com/claude-code)."""

from pathlib import Path

from bands.engines.base import EngineSpec


class ClaudeCodeEngine(EngineSpec):
    def __init__(self) -> None:
        super().__init__(
            name="claude",
            binary="claude",
            default_models={"smart": "sonnet", "fast": "haiku"},
        )

    def command(self, prompt, model, cwd, allowed_tools):
        argv = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
        if model:
            argv += ["--model", model]
        if allowed_tools:
            argv += ["--allowedTools", allowed_tools]
        return argv
