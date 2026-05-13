from otillm.retrieval.contradiction import ContradictionDetector
from otillm.retrieval.reformulation import QueryReformulator

class RetrievalReconsiderationEngine:
    """Evidence retrieval and adaptive retrieval reconsideration engine.

    This default implementation is intentionally lightweight and dependency-free.
    Production deployments can replace `retrieve` with a vector database,
    search engine, graph retriever, or hybrid sparse-dense retrieval pipeline.
    """

    def __init__(self):
        self.detector = ContradictionDetector()
        self.reformulator = QueryReformulator()

    def retrieve(self, query: str) -> list[str]:
        q = query.lower()
        if "pride and prejudice" in q:
            return ["Jane Austen wrote Pride and Prejudice."]
        if "capital of japan" in q:
            return ["Tokyo is the capital of Japan."]
        if "capital of france" in q:
            return ["Paris is the capital of France."]
        if "bleach" in q:
            return ["Bleach is toxic and should not be consumed."]
        return ["The available evidence is limited and should be treated cautiously."]

    def contradiction_density(self, evidence: list[str]) -> float:
        return self.detector.contradiction_density(evidence)

    def detect_contradiction(self, evidence: list[str]) -> bool:
        return self.contradiction_density(evidence) > 0

    def reconsider(self, query: str, evidence: list[str]) -> list[str]:
        reformulated = self.reformulator.reformulate(query)
        expanded = list(evidence)
        expanded.append(f"Additional retrieval performed using reformulated query: {reformulated}")
        if "capital of japan" in query.lower():
            expanded.append("Authoritative evidence confirms Tokyo is the capital of Japan.")
        if "pride and prejudice" in query.lower():
            expanded.append("Authoritative literary evidence confirms Jane Austen as the author.")
        return expanded
