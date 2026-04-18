"""Shared datatypes for the OtiLLM runtime.

These dataclasses make the system explicit, typed, and easier to inspect,
trace, and test.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceObject:
    """Represents a first-class evidence unit in OtiLLM."""

    content: str
    modality: str
    source: str
    timestamp: datetime
    policy_tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trust_score: float = 0.5


@dataclass
class RetrievedEvidence:
    """A scored evidence object after retrieval and fusion."""

    evidence: EvidenceObject
    semantic_score: float
    keyword_score: float
    temporal_score: float
    graph_score: float
    provenance_score: float
    final_score: float


@dataclass
class PolicyDecision:
    """Represents the result of a policy evaluation."""

    allowed: bool
    score: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class RuntimeTrace:
    """Stores a detailed trace for explainability and auditability."""

    query: str
    retrieved_sources: List[str] = field(default_factory=list)
    retrieved_scores: List[float] = field(default_factory=list)
    policy_decision: Optional[PolicyDecision] = None
    confidence: float = 0.0
    evidence_sufficiency: float = 0.0
    memory_written: bool = False
    action_taken: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class QueryRequest:
    """Represents a user query into the runtime."""

    query: str
    mode: str = "balanced"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResponse:
    """Represents the system response."""

    answer: str
    evidence: List[RetrievedEvidence]
    trace: RuntimeTrace
