from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class MemoryRecord:
    query: str
    answer: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class GovernedMemory:
    """Confidence-gated and governance-aware runtime memory."""

    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold
        self.records: List[MemoryRecord] = []

    def maybe_write(self, query: str, answer: str, confidence: float, governance_ok: bool) -> bool:
        if governance_ok and confidence >= self.threshold:
            self.records.append(MemoryRecord(query=query, answer=answer, confidence=confidence))
            return True
        return False

    def search(self, query: str) -> List[MemoryRecord]:
        q = query.lower()
        return [r for r in self.records if q in r.query.lower() or q in r.answer.lower()]
