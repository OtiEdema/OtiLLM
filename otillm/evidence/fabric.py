from dataclasses import dataclass

@dataclass
class EvidenceItem:
    text: str
    relevance: float = 1.0
    freshness: float = 1.0
    source_reliability: float = 1.0
    contradiction_density: float = 0.0

class EvidenceFabric:
    """Evidence quality scoring and governance-aware evidence preparation."""

    def score(self, item: EvidenceItem, alpha=0.4, beta=0.2, gamma=0.3, delta=0.5) -> float:
        return (
            alpha * item.relevance
            + beta * item.freshness
            + gamma * item.source_reliability
            - delta * item.contradiction_density
        )
