from otillm.retrieval import RetrievalReconsiderationEngine

def test_retrieval_returns_evidence():
    engine = RetrievalReconsiderationEngine()
    evidence = engine.retrieve("What is the capital of Japan?")
    assert evidence
