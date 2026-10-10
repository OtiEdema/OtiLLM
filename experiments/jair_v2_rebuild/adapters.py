"""System adapters for the unified JAIR harness."""

from dataclasses import asdict
from datetime import datetime
from time import perf_counter
from typing import Dict, List

from trace_schema import common_trace_completeness


class OtiLLMAdapter:
    def __init__(self, name: str, mode: str, backend):
        self.name = name
        self.mode = mode
        self.backend = backend

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        from otillm import OtiLLM

        runtime = OtiLLM(generator_backend=self.backend)
        for item in evidence:
            metadata = dict(item.get("metadata") or {})
            timestamp = metadata.get("timestamp") or item.get("timestamp")
            parsed_timestamp = None
            if isinstance(timestamp, str) and timestamp:
                try:
                    parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    metadata["timestamp_parse_error"] = timestamp
            runtime.add_evidence(
                content=item["content"],
                source=item.get("source", "manifest"),
                trust_score=float(item.get("trust_score", 0.5)),
                metadata=metadata,
                timestamp=parsed_timestamp,
            )

        start = perf_counter()
        response = runtime.query(record["query"], mode=self.mode)
        elapsed = perf_counter() - start

        trace = asdict(response.trace)
        generation = getattr(runtime.generator, "last_generation_result", None)
        common_trace = {
            "query_received": True,
            "retrieval_attempted": True,
            "evidence_selected": bool(response.trace.retrieved_sources),
            "model_invoked": response.trace.action_taken == "EXECUTE",
            "policy_decision_recorded": response.trace.policy_decision is not None,
            "confidence_recorded": True,
            "action_recorded": bool(response.trace.action_taken),
            "final_output_recorded": True,
        }
        return {
            "system": self.name,
            "answer": response.answer,
            "action": response.trace.action_taken,
            "trace": trace,
            "trace_completeness_common": common_trace_completeness(common_trace),
            "retrieved_sources": response.trace.retrieved_sources,
            "evidence_sufficiency": response.trace.evidence_sufficiency,
            "confidence": response.trace.confidence,
            "latency_seconds": (
                getattr(generation, "latency_seconds", None)
                if generation is not None else elapsed
            ),
            "llm_calls": 1 if generation is not None else 0,
            "retrieval_calls": 1,
            "input_tokens": getattr(generation, "input_tokens", None) if generation is not None else None,
            "output_tokens": getattr(generation, "output_tokens", None) if generation is not None else None,
            "api_cost": getattr(generation, "api_cost", None) if generation is not None else None,
        }


class ExternalAdapter:
    def __init__(self, name: str, impl):
        self.name = name
        self.impl = impl

    def run(self, record: Dict, evidence: List[Dict]) -> Dict:
        return self.impl.run(record, evidence)
