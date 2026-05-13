from typing import List

class UncertaintyEngine:
    """Estimates runtime uncertainty from evidence quality and governance risk."""

    def estimate(self, evidence: List[str], contradiction_density: float = 0.0, governance_risk: float = 0.0) -> float:
        if not evidence:
            return 1.0
        evidence_strength = min(1.0, len(evidence) / 5.0)
        uncertainty = 1.0 - evidence_strength + contradiction_density + governance_risk
        return max(0.0, min(1.0, uncertainty))
