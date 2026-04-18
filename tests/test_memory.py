from otillm import OtiLLM, OtiConfig


def test_memory_writes_high_quality_content():
    config = OtiConfig()
    config.thresholds.memory_quality = 0.60
    model = OtiLLM(config=config)
    model.add_evidence("Enterprise AI requires trustworthy evidence.", source="doc1", trust_score=1.0)
    model.add_evidence("Good governance improves deployment reliability.", source="doc2", trust_score=1.0)
    response = model.query("Why is trustworthy evidence important?")
    assert response.trace.memory_written is True
    assert len(model.memory_engine.all()) >= 1
