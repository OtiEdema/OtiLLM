from otillm import OtiLLM


def test_evidence_retrieval_orders_relevant_items_higher():
    model = OtiLLM()
    model.add_evidence("Cats are mammals.", source="doc1", trust_score=0.9)
    model.add_evidence("Quantum circuits use qubits.", source="doc2", trust_score=0.9)
    response = model.query("What are cats?")
    assert response.evidence
    assert response.evidence[0].evidence.source == "doc1"
