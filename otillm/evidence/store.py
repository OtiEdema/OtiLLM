"""Evidence storage."""

from typing import List

from otillm.types import EvidenceObject


class EvidenceStore:
    """Simple in-memory evidence repository."""

    def __init__(self) -> None:
        self._items: List[EvidenceObject] = []

    def add(self, evidence: EvidenceObject) -> None:
        """Add one evidence object to the store."""
        self._items.append(evidence)

    def add_many(self, evidence_list: List[EvidenceObject]) -> None:
        """Add multiple evidence objects to the store."""
        self._items.extend(evidence_list)

    def all(self) -> List[EvidenceObject]:
        """Return all evidence objects."""
        return list(self._items)
