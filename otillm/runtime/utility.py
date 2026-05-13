from dataclasses import dataclass

@dataclass
class UtilityInput:
    informational_value: float
    evidence_support: float
    helpfulness: float
    hallucination_risk: float
    governance_risk: float
    operational_cost: float

class CognitiveUtilityOptimizer:
    """Computes governed cognitive utility for runtime action selection."""

    def score(self, x: UtilityInput) -> float:
        return (
            x.informational_value
            + x.evidence_support
            + x.helpfulness
            - x.hallucination_risk
            - x.governance_risk
            - x.operational_cost
        )

    def select_action(self, utility: float, uncertainty: float, governance_risk: float) -> str:
        if governance_risk >= 0.75:
            return "refuse"
        if uncertainty >= 0.70:
            return "reconsider_retrieval"
        if utility < 0.20:
            return "clarify"
        return "answer"
