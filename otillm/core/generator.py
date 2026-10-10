"""Generator engine for OtiLLM v2.0.

The publication branch supports dependency injection of a common model backend
so OtiLLM can be compared fairly with baselines using the same generator.
If no backend is supplied, the lightweight evidence-formatting fallback is used
for unit tests and offline smoke tests only.
"""

from typing import Any, List, Optional

from otillm.types import RetrievedEvidence


class GeneratorEngine:
    """Generate a response grounded in retrieved evidence."""

    def __init__(self, backend: Optional[Any] = None) -> None:
        self.backend = backend

    @staticmethod
    def _prompt(query: str, evidence: List[RetrievedEvidence]) -> str:
        context = "\n".join(
            f"[{i}] {item.evidence.content} (source={item.evidence.source})"
            for i, item in enumerate(evidence[:5], start=1)
        )
        return (
            "Answer the question using the supplied evidence. "
            "If the evidence is insufficient or conflicting, say so rather than inventing facts.\n"
            f"Question: {query}\nEvidence:\n{context}"
        )

    def generate(self, query: str, evidence: List[RetrievedEvidence]) -> str:
        """Generate an answer using the injected publication backend when configured."""
        if not evidence:
            return "I could not find enough evidence to answer that reliably."

        if self.backend is not None:
            result = self.backend.generate(self._prompt(query, evidence))
            if isinstance(result, str):
                return result
            if hasattr(result, "text"):
                return result.text
            raise TypeError("Injected generator backend must return a string or an object with a .text attribute.")

        top = evidence[0]
        support_lines = [
            f"- {item.evidence.content} (source: {item.evidence.source})"
            for item in evidence[:3]
        ]
        return (
            f"Based on the strongest available evidence, here is a grounded response to your query: '{query}'.\n\n"
            f"Most relevant evidence: {top.evidence.content}\n\n"
            "Supporting evidence:\n" + "\n".join(support_lines)
        )
