from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class RuntimeState:
    """Runtime cognitive state used by the OtiLLM governed runtime."""
    query: str
    evidence: List[str] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    governance: Dict[str, Any] = field(default_factory=dict)
    uncertainty: float = 1.0
    utility: float = 0.0
    action: str = "initialise"

@dataclass
class RuntimeResult:
    """Final governed runtime output."""
    answer: str
    action: str
    confidence: float
    evidence_used: List[str]
    trace: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
