class ContradictionDetector:
    """Lightweight contradiction detector for benchmark and demonstration use."""

    contradiction_pairs = [
        ("tokyo", "osaka"),
        ("jane austen", "charles dickens"),
        ("paris", "berlin"),
        ("100 degrees", "50 degrees"),
    ]

    def contradiction_density(self, evidence: list[str]) -> float:
        text = " ".join(evidence).lower()
        contradictions = 0
        for a, b in self.contradiction_pairs:
            if a in text and b in text:
                contradictions += 1
        if not evidence:
            return 0.0
        return min(1.0, contradictions / max(1, len(evidence)))
