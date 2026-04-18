from otillm.multimodal import PerceptionEngine


def test_multimodal_ingest_preserves_modality():
    engine = PerceptionEngine()
    item = engine.ingest(raw_input={"pixels": [0, 1, 2]}, modality="image", source="img001")
    assert item.modality == "image"
    assert item.source == "img001"
    assert "pixels" in item.content
