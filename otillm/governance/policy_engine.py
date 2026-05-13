from dataclasses import dataclass
from typing import List

@dataclass
class GovernanceState:
    allowed: bool
    risk: float
    reason: str
    requires_reconsideration: bool = False

class PolicyEngine:
    """Policy-aware runtime governance engine."""

    unsafe_terms = {
        "make ransomware",
        "build malware",
        "drink bleach",
        "guaranteed medical diagnosis",
    }

    def evaluate(self, query: str, evidence: List[str]) -> GovernanceState:
        q = query.lower()
        if any(term in q for term in self.unsafe_terms):
            return GovernanceState(
                allowed=False,
                risk=0.95,
                reason="policy_block",
                requires_reconsideration=False,
            )

        if not evidence:
            return GovernanceState(
                allowed=True,
                risk=0.25,
                reason="insufficient_evidence",
                requires_reconsideration=True,
            )

        return GovernanceState(
            allowed=True,
            risk=0.05,
            reason="policy_ok",
            requires_reconsideration=False,
        )
