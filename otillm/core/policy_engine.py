"""Policy engine for runtime governance."""

from otillm.config import OtiConfig
from otillm.types import PolicyDecision
from otillm.utils import safe_contains


class PolicyEngine:
    """Evaluate requests against runtime policies."""

    def __init__(self, config: OtiConfig) -> None:
        self.config = config

    def evaluate(self, query: str) -> PolicyDecision:
        """Evaluate whether a query is allowed."""
        reasons = []
        score = 1.0

        if safe_contains(query, self.config.blocked_terms):
            reasons.append("Blocked or high-risk terms detected.")
            score -= 0.7

        allowed = score >= self.config.thresholds.policy
        if allowed:
            reasons.append("Policy check passed.")
        else:
            reasons.append("Policy threshold not met.")
        return PolicyDecision(allowed=allowed, score=max(0.0, score), reasons=reasons)
