class GovernanceScorer:
    """Weighted policy-risk scorer."""

    def score(self, violation_probabilities: list[float], weights: list[float] | None = None) -> float:
        if not violation_probabilities:
            return 0.0
        if weights is None:
            weights = [1.0] * len(violation_probabilities)
        total_weight = sum(weights) or 1.0
        return min(1.0, sum(p * w for p, w in zip(violation_probabilities, weights)) / total_weight)
