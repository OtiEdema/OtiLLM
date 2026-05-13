from dataclasses import dataclass, field
from typing import Any, Dict, List
import json

@dataclass
class RuntimeTraceGraph:
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    def add_node(self, node_id: str, node_type: str, payload: Dict[str, Any]) -> None:
        self.nodes.append({"id": node_id, "type": node_type, "payload": payload})

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.edges.append({"source": source, "target": target, "relation": relation})

    def to_dict(self) -> Dict[str, Any]:
        return {"nodes": self.nodes, "edges": self.edges}

    def summary(self) -> str:
        return f"ERRG(nodes={len(self.nodes)}, edges={len(self.edges)})"

    def export(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

class ERRGBuilder:
    """Builds Explainable Runtime Reasoning Graphs."""

    def create_graph(
        self,
        query: str,
        evidence: list[str],
        governance_events: list[str],
        uncertainty_score: float,
        action: str = "answer",
    ) -> RuntimeTraceGraph:
        graph = RuntimeTraceGraph()
        graph.add_node("query", "query", {"text": query})
        graph.add_node("evidence", "evidence", {"items": evidence})
        graph.add_node("governance", "governance", {"events": governance_events})
        graph.add_node("uncertainty", "uncertainty", {"score": uncertainty_score})
        graph.add_node("action", "action", {"selected": action})
        graph.add_edge("query", "evidence", "retrieves")
        graph.add_edge("evidence", "governance", "evaluated_by")
        graph.add_edge("governance", "uncertainty", "updates")
        graph.add_edge("uncertainty", "action", "conditions")
        return graph
