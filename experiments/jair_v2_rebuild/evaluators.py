"""Evaluator interfaces for independent content-quality assessment."""

from typing import Dict, List, Optional, Protocol


class FaithfulnessEvaluator(Protocol):
    name: str

    def score(self, answer: str, evidence: List[Dict]) -> Dict:
        """Return claim_count, supported_claim_count, faithfulness, unsupported_claim_rate."""
        ...


class FactualityEvaluator(Protocol):
    name: str

    def score(self, answer: str, references: List[str], metadata: Dict) -> Optional[float]:
        ...


class UnconfiguredFaithfulnessEvaluator:
    name = "unconfigured"

    def score(self, answer: str, evidence: List[Dict]) -> Dict:
        return {
            "claim_count": None,
            "supported_claim_count": None,
            "faithfulness": None,
            "unsupported_claim_rate": None,
        }


class UnconfiguredFactualityEvaluator:
    name = "unconfigured"

    def score(self, answer: str, references: List[str], metadata: Dict) -> Optional[float]:
        return None
