"""Generator engine.

This module intentionally provides a policy-safe, evidence-grounded baseline
response generator that works without requiring a heavyweight external model.
"""

from typing import List

from otillm.types import RetrievedEvidence


class GeneratorEngine:
    """Generate a grounded response using retrieved evidence."""

    def generate(self, query: str, evidence: List[RetrievedEvidence]) -> str:
        """Generate an answer grounded in the top evidence."""
        if not evidence:
            return "I could not find enough evidence to answer that reliably."

        top = evidence[0]
        support_lines = []
        for item in evidence[:3]:
            support_lines.append(f"- {item.evidence.content} (source: {item.evidence.source})")

        answer = (
            f"Based on the strongest available evidence, here is a grounded response to your query: '{query}'.\n\n"
            f"Most relevant evidence: {top.evidence.content}\n\n"
            f"Supporting evidence:\n" + "\n".join(support_lines)
        )
        return answer
