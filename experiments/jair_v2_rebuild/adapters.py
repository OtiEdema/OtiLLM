"""System adapters for the unified JAIR harness."""

from dataclasses import asdict
from time import perf_counter
from typing import Dict, List


class OtiLLMAdapter:
    def __init__(self, name: str, mode: str, backend):
        self.name = name
        self.mode = mode
        self.backend = backend

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        from otillm.runtime import OtiLLM

        runtime = OtiLLM(generator_backend=self.backend)
        for item in evidence:
            runtime.add_evidence(
                content=item["content"],
                source=item.get("source", "manifest"),
                trust_score=float(item.get("trust_score", 0.5)),
            )

        start = perf_counter()
        response = runtime.query(record["query"], mode=self.mode)
        elapsed = perf_counter() - start

        trace = asdict(response.trace)
        return {
            "system": self.name,
            "answer": response.answer,
            "action": response.trace.action_taken,
            "trace": trace,
            "retrieved_sources": response.trace.retrieved_sources,
            "evidence_sufficiency": response.trace.evidence_sufficiency,
            "confidence": response.trace.confidence,
            "latency_seconds": elapsed,
            "llm_calls": 1 if response.trace.action_taken == "EXECUTE" else 0,
            "retrieval_calls": 1,
            "input_tokens": None,
            "output_tokens": None,
            "api_cost": None,
        }


class ExternalAdapter:
    def __init__(self, name: str, impl):
        self.name = name
        self.impl = impl

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        return self.impl.run(record, evidence)
