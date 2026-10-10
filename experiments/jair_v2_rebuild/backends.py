"""Backend protocol and factory for fair JAIR system comparisons."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Protocol


@dataclass
class GenerationResult:
    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_seconds: Optional[float] = None
    api_cost: Optional[float] = None
    raw: Optional[Dict] = None


class ModelBackend(Protocol):
    name: str
    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> GenerationResult: ...


class UnconfiguredBackend:
    name = "unconfigured"
    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> GenerationResult:
        raise RuntimeError(
            "No publication model backend is configured. Set the exact provider/model, "
            "archive its parameters, and then enable model-based systems."
        )


class SmokeBackend:
    """Deterministic backend for pipeline tests only; never use for paper results."""
    name = "smoke-test-backend"
    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> GenerationResult:
        p = prompt.lower()
        if "pride and prejudice" in p:
            text = "Jane Austen"
        elif "capital of japan" in p:
            text = "Tokyo"
        else:
            text = "Insufficient evidence."
        return GenerationResult(text=text, input_tokens=None, output_tokens=None, latency_seconds=0.0, api_cost=0.0)


def load_backend(config_path: str):
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    kind = cfg.get("kind", "unconfigured")
    if kind == "smoke":
        return SmokeBackend()
    if kind == "unconfigured":
        return UnconfiguredBackend()
    raise RuntimeError(
        f"Backend kind {kind!r} is not implemented in the publication branch. "
        "Add a provider adapter only after the exact model/version is selected."
    )
