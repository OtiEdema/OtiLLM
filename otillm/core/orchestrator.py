"""Cognitive orchestrator."""

from typing import List

from otillm.config import OtiConfig
from otillm.core.generator import GeneratorEngine
from otillm.core.memory_engine import MemoryEngine
from otillm.core.policy_engine import PolicyEngine
from otillm.evidence.fusion import EvidenceFusionEngine
from otillm.evidence.retrieval import EvidenceRetriever
from otillm.types import EvidenceObject, QueryRequest, QueryResponse, RuntimeTrace


class CognitiveOrchestrator:
    """Main bounded orchestration engine."""

    def __init__(
        self,
        config: OtiConfig,
        policy_engine: PolicyEngine,
        memory_engine: MemoryEngine,
        retriever: EvidenceRetriever,
        fusion_engine: EvidenceFusionEngine,
        generator: GeneratorEngine,
    ) -> None:
        self.config = config
        self.policy_engine = policy_engine
        self.memory_engine = memory_engine
        self.retriever = retriever
        self.fusion_engine = fusion_engine
        self.generator = generator

    def _estimate_confidence(self, evidence_sufficiency: float, policy_score: float) -> float:
        """Estimate response confidence from evidence and policy posture."""
        return min(1.0, 0.65 * evidence_sufficiency + 0.35 * policy_score)

    def run(self, request: QueryRequest, corpus: List[EvidenceObject]) -> QueryResponse:
        """Execute the full OtiLLM runtime path."""
        trace = RuntimeTrace(query=request.query)
        policy = self.policy_engine.evaluate(request.query)
        trace.policy_decision = policy

        if not policy.allowed:
            trace.action_taken = "BLOCK"
            trace.notes.extend(policy.reasons)
            return QueryResponse(answer=self.config.safe_default_response, evidence=[], trace=trace)

        evidence = self.retriever.retrieve(request.query, corpus)
        trace.retrieved_sources = [e.evidence.source for e in evidence]
        trace.retrieved_scores = [e.final_score for e in evidence]

        evidence_sufficiency = self.fusion_engine.estimate_sufficiency(evidence)
        trace.evidence_sufficiency = evidence_sufficiency

        confidence = self._estimate_confidence(evidence_sufficiency, policy.score)
        trace.confidence = confidence

        if evidence_sufficiency < self.config.thresholds.evidence:
            trace.action_taken = "REFINE_OR_DEFER"
            trace.notes.append("Evidence threshold not met.")
            return QueryResponse(
                answer="I found some evidence, but not enough to answer reliably. Please refine the question or add more trusted sources.",
                evidence=evidence,
                trace=trace,
            )

        if confidence < self.config.thresholds.confidence:
            trace.action_taken = "DEFER_LOW_CONFIDENCE"
            trace.notes.append("Confidence threshold not met.")
            return QueryResponse(
                answer="I have some relevant information, but my confidence is too low to provide a strong answer.",
                evidence=evidence,
                trace=trace,
            )

        answer = self.generator.generate(request.query, evidence)
        trace.action_taken = "EXECUTE"

        memory_written = self.memory_engine.write(answer, quality_score=confidence, policy=policy)
        trace.memory_written = memory_written
        if memory_written:
            trace.notes.append("Answer written to memory.")
        else:
            trace.notes.append("Answer not written to memory.")

        return QueryResponse(answer=answer, evidence=evidence, trace=trace)
