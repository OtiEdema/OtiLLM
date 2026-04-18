"""Multimodal perception layer."""

from datetime import datetime, timezone
from typing import Any

from otillm.types import EvidenceObject


class PerceptionEngine:
    """Perception layer for turning raw inputs into EvidenceObjects."""

    def ingest(self, raw_input: Any, modality: str = "text", source: str = "inline") -> EvidenceObject:
        """Convert raw input into a typed EvidenceObject."""
        content = raw_input if isinstance(raw_input, str) else str(raw_input)
        return EvidenceObject(
            content=content,
            modality=modality,
            source=source,
            timestamp=datetime.now(timezone.utc),
            policy_tags=[modality],
            metadata={"ingested_by": "PerceptionEngine"},
            trust_score=0.5,
        )
