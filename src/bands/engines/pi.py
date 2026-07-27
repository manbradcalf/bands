"""pi engine (https://pi.dev)."""

from bands.engines.base import EngineSpec

# pi tool names (see `pi --help` --tools). Claude-style names mapped here.
PI_TOOLS = "read,write,edit,bash"


class PiEngine(EngineSpec):
    def __init__(self) -> None:
        super().__init__(
            name="pi",
            binary="pi",
            # No defaults: pi resolves models itself (--model or its own config).
            default_models={"smart": None, "fast": None},
        )

    def command(self, prompt, model, cwd, allowed_tools):
        argv = ["pi", "-p", prompt, "--mode", "json", "--no-session"]
        if model:
            argv += ["--model", model]
        if allowed_tools:
            # Bands' scripts pass Claude-style tool names; pi wants its own.
            argv += ["--tools", PI_TOOLS]
        return argv
