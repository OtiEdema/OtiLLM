"""Configuration models for OtiLLM 3.0.

This file centralises all tunable runtime parameters.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RetrievalWeights:
    """Weights used by the Evidence Fabric fusion stage."""

    semantic: float = 0.45
    keyword: float = 0.20
    temporal: float = 0.15
    graph: float = 0.10
    provenance: float = 0.10


@dataclass
class Thresholds:
    """Thresholds controlling runtime behaviour."""

    confidence: float = 0.55
    evidence: float = 0.40
    policy: float = 0.50
    memory_quality: float = 0.65


@dataclass
class OtiConfig:
    """Main runtime configuration."""

    top_k: int = 5
    retrieval_weights: RetrievalWeights = field(default_factory=RetrievalWeights)
    thresholds: Thresholds = field(default_factory=Thresholds)
    blocked_terms: List[str] = field(default_factory=lambda: ["malware", "exploit", "steal password"])
    safe_default_response: str = (
        "I cannot complete that request in its current form. "
        "I can help with a safer, policy-compliant alternative."
    )
    max_memory_items: int = 5000
