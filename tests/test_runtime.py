from otillm import OtiLLM


def test_runtime_returns_explanation_trace():
    model = OtiLLM()
    model.add_evidence("OtiLLM is evidence-native.", source="doc1", trust_score=0.9)
    response = model.query("What is OtiLLM?")
    explanation = model.explain(response)
    assert "OtiLLM Trace Report" in explanation
    assert "Retrieved Sources" in explanation
