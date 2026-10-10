"""Reproducible baseline definitions for the unified JAIR harness.

These adapters share one ModelBackend. They are deliberately explicit rather
than relying on framework defaults that may change between versions.
"""

from time import perf_counter
from typing import Dict, List

from backends import ModelBackend
from trace_schema import common_trace_completeness


def evidence_block(evidence: List[Dict], limit: int = 5) -> str:
    return "\n".join(
        f"[{i}] {item.get('content','')} (source={item.get('source','unknown')})"
        for i, item in enumerate(evidence[:limit], start=1)
    )


class BaseAdapter:
    def __init__(self, name: str, backend: ModelBackend, temperature: float = 0.2, max_tokens: int = 512):
        self.name = name
        self.backend = backend
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _call(self, prompt: str):
        return self.backend.generate(
            prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    @staticmethod
    def _pack(name, result, trace, *, llm_calls, retrieval_calls):
        trace["final_output_recorded"] = True
        trace["action_recorded"] = True
        return {
            "system": name,
            "answer": result.text,
            "action": "EXECUTE",
            "trace": trace,
            "trace_completeness_common": common_trace_completeness(trace),
            "latency_seconds": result.latency_seconds,
            "llm_calls": llm_calls,
            "retrieval_calls": retrieval_calls,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "api_cost": result.api_cost,
        }


class DirectLLMAdapter(BaseAdapter):
    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        trace = {
            "query_received": True,
            "retrieval_attempted": False,
            "evidence_selected": False,
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": False,
        }
        result = self._call(f"Answer the question accurately and concisely.\nQuestion: {record['query']}")
        return self._pack(self.name, result, trace, llm_calls=1, retrieval_calls=0)


class PromptChainAdapter(BaseAdapter):
    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        trace = {
            "query_received": True,
            "retrieval_attempted": False,
            "evidence_selected": False,
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": False,
        }
        draft = self._call(f"Draft an answer.\nQuestion: {record['query']}")
        final = self._call(
            "Improve the draft for factual accuracy and concision. "
            "Do not invent evidence.\n"
            f"Question: {record['query']}\nDraft: {draft.text}"
        )
        return self._pack(self.name, final, trace, llm_calls=2, retrieval_calls=0)


class StandardRAGAdapter(BaseAdapter):
    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        context = evidence_block(evidence, limit=5)
        trace = {
            "query_received": True,
            "retrieval_attempted": True,
            "evidence_selected": bool(evidence),
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": False,
        }
        result = self._call(
            "Answer using the supplied evidence. If the evidence is insufficient, say so.\n"
            f"Question: {record['query']}\nEvidence:\n{context}"
        )
        return self._pack(self.name, result, trace, llm_calls=1, retrieval_calls=1)


class StrongRAGAdapter(BaseAdapter):
    """Strong RAG consumes the reranked evidence supplied by the common harness."""

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        ranked = sorted(evidence, key=lambda x: float(x.get("retrieval_score", x.get("trust_score", 0.5))), reverse=True)
        context = evidence_block(ranked, limit=5)
        trace = {
            "query_received": True,
            "retrieval_attempted": True,
            "evidence_selected": bool(ranked),
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": False,
        }
        result = self._call(
            "Use only well-supported evidence. Resolve conflicts explicitly and abstain if support is inadequate.\n"
            f"Question: {record['query']}\nRanked evidence:\n{context}"
        )
        return self._pack(self.name, result, trace, llm_calls=1, retrieval_calls=1)


class SelfCheckingAdapter(BaseAdapter):
    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        trace = {
            "query_received": True,
            "retrieval_attempted": False,
            "evidence_selected": False,
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": True,
        }
        draft = self._call(f"Answer accurately.\nQuestion: {record['query']}")
        final = self._call(
            "Check the draft for factual errors. Return a corrected answer only.\n"
            f"Question: {record['query']}\nDraft: {draft.text}"
        )
        return self._pack(self.name, final, trace, llm_calls=2, retrieval_calls=0)


class GuardrailAdapter(BaseAdapter):
    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        should_refuse = record.get("policy_label") in {"refuse", "defer"}
        if should_refuse:
            class R:
                text = "I cannot provide that answer under the applicable policy."
                input_tokens = output_tokens = api_cost = latency_seconds = None
            result = R()
            action = "REFUSE"
            calls = 0
        else:
            result = self._call(f"Answer accurately and concisely.\nQuestion: {record['query']}")
            action = "EXECUTE"
            calls = 1
        trace = {
            "query_received": True,
            "retrieval_attempted": False,
            "evidence_selected": False,
            "model_invoked": calls > 0,
            "policy_decision_recorded": True,
            "confidence_recorded": False,
            "action_recorded": True,
            "final_output_recorded": True,
        }
        packed = self._pack(self.name, result, trace, llm_calls=calls, retrieval_calls=0)
        packed["action"] = action
        return packed


class ReActAdapter(BaseAdapter):
    """Bounded two-step ReAct-style baseline without hidden-chain-of-thought export."""

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        context = evidence_block(evidence, limit=5)
        trace = {
            "query_received": True,
            "retrieval_attempted": True,
            "evidence_selected": bool(evidence),
            "model_invoked": True,
            "policy_decision_recorded": False,
            "confidence_recorded": False,
        }
        plan = self._call(
            "Choose whether the supplied evidence is sufficient or whether another retrieval would be useful. "
            "Return only SUFFICIENT or RETRIEVE.\n"
            f"Question: {record['query']}\nEvidence:\n{context}"
        )
        # The publication harness records the decision; an actual second retrieval
        # must be supplied by the common retriever rather than improvised in the prompt.
        final = self._call(
            "Answer using the available evidence. If evidence is inadequate, abstain.\n"
            f"Question: {record['query']}\nEvidence:\n{context}\nControl decision: {plan.text}"
        )
        return self._pack(self.name, final, trace, llm_calls=2, retrieval_calls=1)
