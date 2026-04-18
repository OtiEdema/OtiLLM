"""Main public runtime wrapper for OtiLLM 3.0."""

from typing import Iterable, Optional

from otillm.config import OtiConfig
from otillm.core import CognitiveOrchestrator, GeneratorEngine, MemoryEngine, PolicyEngine
from otillm.evidence import EvidenceFusionEngine, EvidenceRetriever, EvidenceStore
from otillm.explainability import TraceFormatter
from otillm.multimodal import PerceptionEngine
from otillm.types import EvidenceObject, QueryRequest, QueryResponse


class OtiLLM:
    """Main entrypoint for the OtiLLM 3.0 runtime."""

    def __init__(self, config: Optional[OtiConfig] = None) -> None:
        self.config = config or OtiConfig()
        self.perception = PerceptionEngine()
        self.store = EvidenceStore()
        self.policy_engine = PolicyEngine(self.config)
        self.memory_engine = MemoryEngine(self.config)
        self.retriever = EvidenceRetriever(self.config)
        self.fusion_engine = EvidenceFusionEngine()
        self.generator = GeneratorEngine()
        self.orchestrator = CognitiveOrchestrator(
            config=self.config,
            policy_engine=self.policy_engine,
            memory_engine=self.memory_engine,
            retriever=self.retriever,
            fusion_engine=self.fusion_engine,
            generator=self.generator,
        )
        self.trace_formatter = TraceFormatter()

    def add_evidence(self, content: str, modality: str = "text", source: str = "inline", trust_score: float = 0.5) -> EvidenceObject:
        """Add one item into the evidence fabric."""
        evidence = self.perception.ingest(content, modality=modality, source=source)
        evidence.trust_score = trust_score
        self.store.add(evidence)
        return evidence

    def add_evidence_batch(self, items: Iterable[dict]) -> None:
        """Add a batch of evidence items."""
        for item in items:
            self.add_evidence(
                content=item["content"],
                modality=item.get("modality", "text"),
                source=item.get("source", "batch"),
                trust_score=item.get("trust_score", 0.5),
            )

    def query(self, query: str, mode: str = "balanced", user_id: Optional[str] = None, session_id: Optional[str] = None) -> QueryResponse:
        """Query the runtime and return a structured response."""
        request = QueryRequest(query=query, mode=mode, user_id=user_id, session_id=session_id)
        return self.orchestrator.run(request=request, corpus=self.store.all())

    def explain(self, response: QueryResponse) -> str:
        """Return a formatted explanation of a prior response."""
        return self.trace_formatter.explain(response)
