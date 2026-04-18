"""Memory engine with gated writes."""

from collections import deque
from dataclasses import dataclass
from typing import Deque, List

from otillm.config import OtiConfig
from otillm.types import PolicyDecision
from otillm.utils import normalize_text


@dataclass
class MemoryItem:
    """Represents one stored memory item."""

    content: str
    quality_score: float


class MemoryEngine:
    """Tiered memory engine for the starter release."""

    def __init__(self, config: OtiConfig) -> None:
        self.config = config
        self._memory: Deque[MemoryItem] = deque(maxlen=config.max_memory_items)

    def all(self) -> List[MemoryItem]:
        """Return current memory contents."""
        return list(self._memory)

    def _novelty(self, content: str) -> float:
        """Estimate novelty by comparing normalized text overlap."""
        norm = normalize_text(content)
        if not self._memory:
            return 1.0
        exact_match = any(normalize_text(item.content) == norm for item in self._memory)
        return 0.0 if exact_match else 1.0

    def should_write(self, content: str, quality_score: float, policy: PolicyDecision) -> bool:
        """Decide whether memory should be written."""
        novelty = self._novelty(content)
        return quality_score >= self.config.thresholds.memory_quality and policy.allowed and novelty > 0.0

    def write(self, content: str, quality_score: float, policy: PolicyDecision) -> bool:
        """Write content into memory if allowed."""
        if self.should_write(content, quality_score, policy):
            self._memory.append(MemoryItem(content=content, quality_score=quality_score))
            return True
        return False
