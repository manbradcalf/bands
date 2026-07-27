"""Engine registry."""

from bands.engines.base import EngineSpec, UnknownEngineError
from bands.engines.claude_code import ClaudeCodeEngine
from bands.engines.pi import PiEngine

_ENGINES: dict[str, EngineSpec] = {e.name: e for e in (ClaudeCodeEngine(), PiEngine())}


def get_engine(name: str) -> EngineSpec:
    try:
        return _ENGINES[name]
    except KeyError:
        raise UnknownEngineError(
            f"unknown engine {name!r}; available: {', '.join(sorted(_ENGINES))}"
        ) from None


def engine_names() -> list[str]:
    return sorted(_ENGINES)


__all__ = ["EngineSpec", "UnknownEngineError", "get_engine", "engine_names"]
