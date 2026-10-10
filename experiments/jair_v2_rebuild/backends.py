"""Backend protocol for fair cross-system JAIR evaluation.

All LLM-based systems must share the same configured backend for a controlled
comparison unless the experiment explicitly studies model routing.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol


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

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> GenerationResult:
        ...


class UnconfiguredBackend:
    """Fail-closed backend used until the exact publication backend is archived."""

    name = "unconfigured"

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> GenerationResult:
        raise RuntimeError(
            "No publication model backend is configured. "
            "Set the exact model/provider and archive its parameters before enabling external baselines."
        )
