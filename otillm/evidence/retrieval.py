"""Evidence retrieval layer."""

from datetime import datetime, timezone
from math import exp
from typing import List

from otillm.config import OtiConfig
from otillm.types import EvidenceObject, RetrievedEvidence
from otillm.utils import tokenize_simple


class EvidenceRetriever:
    """Hybrid retriever for evidence objects."""

    def __init__(self, config: OtiConfig) -> None:
        self.config = config

    @staticmethod
    def _semantic_score(query: str, content: str) -> float:
        q = set(tokenize_simple(query))
        c = set(tokenize_simple(content))
        if not q or not c:
            return 0.0
        return len(q & c) / len(q | c)

    @staticmethod
    def _keyword_score(query: str, content: str) -> float:
        q_tokens = tokenize_simple(query)
        c_tokens = tokenize_simple(content)
        if not q_tokens:
            return 0.0
        overlap = sum(1 for t in q_tokens if t in c_tokens)
        return overlap / max(1, len(q_tokens))

    @staticmethod
    def _temporal_score(timestamp: datetime) -> float:
        now = datetime.now(timezone.utc) if timestamp.tzinfo else datetime.utcnow()
        delta_days = abs((now - timestamp).total_seconds()) / 86400.0
        return exp(-delta_days / 30.0)

    @staticmethod
    def _graph_score(evidence: EvidenceObject, query: str) -> float:
        entities = evidence.metadata.get("entities", [])
        q_tokens = set(tokenize_simple(query))
        if not entities:
            return 0.0
        overlap = len(q_tokens.intersection({str(e).lower() for e in entities}))
        return overlap / max(1, len(entities))

    @staticmethod
    def _provenance_score(evidence: EvidenceObject) -> float:
        return max(0.0, min(1.0, evidence.trust_score))

    def retrieve(self, query: str, corpus: List[EvidenceObject]) -> List[RetrievedEvidence]:
        weights = self.config.retrieval_weights
        results: List[RetrievedEvidence] = []

        for item in corpus:
            semantic = self._semantic_score(query, item.content)
            keyword = self._keyword_score(query, item.content)
            temporal = self._temporal_score(item.timestamp)
            graph = self._graph_score(item, query)
            provenance = self._provenance_score(item)
            final = (
                weights.semantic * semantic
                + weights.keyword * keyword
                + weights.temporal * temporal
                + weights.graph * graph
                + weights.provenance * provenance
            )
            results.append(
                RetrievedEvidence(
                    evidence=item,
                    semantic_score=semantic,
                    keyword_score=keyword,
                    temporal_score=temporal,
                    graph_score=graph,
                    provenance_score=provenance,
                    final_score=final,
                )
            )
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results[: self.config.top_k]
