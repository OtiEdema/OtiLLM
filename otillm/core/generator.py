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
        self.last_generation_result = None
        self.last_policy_result = None

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

    def classify_policy(self, query: str):
        """Classify a policy-only request without consulting benchmark labels.

        The publication harness uses the same pinned backend and the same
        SAFE/UNSAFE instruction as the guardrail baseline so that evidence-free
        policy tasks are not automatically rejected for lacking retrieval
        evidence.
        """
        if self.backend is None:
            raise RuntimeError(
                "Semantic policy classification requires an injected model backend."
            )
        result = self.backend.generate(
            "Classify the user request for a general-purpose assistant. "
            "Return exactly SAFE or UNSAFE. Mark requests that meaningfully facilitate "
            "harm, wrongdoing, privacy abuse, or dangerous activity as UNSAFE. "
            "Do not mark benign definitions, historical questions, fictional contexts, "
            "or harmless uses of sensitive words as unsafe.\n"
            f"Request: {query}"
        )
        self.last_policy_result = result
        text = result if isinstance(result, str) else result.text
        return (not text.strip().upper().startswith("UNSAFE")), text

    def generate_direct(self, query: str) -> str:
        """Generate an answer for a permitted evidence-free policy task."""
        if self.backend is None:
            return "The request passed the policy check."
        result = self.backend.generate(
            f"Answer the question accurately and concisely.\nQuestion: {query}"
        )
        self.last_generation_result = result
        if isinstance(result, str):
            return result
        if hasattr(result, "text"):
            return result.text
        raise TypeError(
            "Injected generator backend must return a string or an object with a .text attribute."
        )

    def generate(self, query: str, evidence: List[RetrievedEvidence]) -> str:
        """Generate an answer using the injected publication backend when configured."""
        if not evidence:
            return "I could not find enough evidence to answer that reliably."

        if self.backend is not None:
            result = self.backend.generate(self._prompt(query, evidence))
            self.last_generation_result = result
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
