"""Evidence fusion and sufficiency estimation."""

from typing import List

from otillm.types import RetrievedEvidence


class EvidenceFusionEngine:
    """Fuse retrieved evidence and estimate sufficiency."""

    def estimate_sufficiency(self, evidence: List[RetrievedEvidence]) -> float:
        if not evidence:
            return 0.0
        avg_score = sum(e.final_score for e in evidence) / len(evidence)
        unique_sources = len({e.evidence.source for e in evidence})
        diversity_bonus = min(0.2, unique_sources * 0.03)
        return min(1.0, avg_score + diversity_bonus)

    def compile_context(self, evidence: List[RetrievedEvidence]) -> str:
        lines = []
        for idx, item in enumerate(evidence, start=1):
            lines.append(f"[{idx}] Source={item.evidence.source} | Content={item.evidence.content}")
        return "\n".join(lines)
