"""Top-level package for OtiLLM 0.1.0.

This module exposes the main runtime class and key data structures so that
users can import them directly from `otillm`.
"""

from .config import OtiConfig
from .types import (
    EvidenceObject,
    PolicyDecision,
    QueryRequest,
    QueryResponse,
    RetrievedEvidence,
    RuntimeTrace,
)
from .runtime import OtiLLM

__all__ = [
    "OtiConfig",
    "EvidenceObject",
    "PolicyDecision",
    "QueryRequest",
    "QueryResponse",
    "RetrievedEvidence",
    "RuntimeTrace",
    "OtiLLM",
]

__version__ = "0.1.0"
