from otillm.retrieval import RetrievalReconsiderationEngine

engine = RetrievalReconsiderationEngine()
query = "What is the capital of Japan?"
evidence = engine.retrieve(query)

if engine.detect_contradiction(evidence):
    evidence = engine.reconsider(query, evidence)

print(evidence)
