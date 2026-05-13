class RuntimeDecisionRouter:
    """Routes runtime actions to appropriate subsystems."""

    def route(self, action: str) -> str:
        mapping = {
            "answer": "generator",
            "reconsider_retrieval": "retrieval",
            "clarify": "clarification",
            "refuse": "governance",
        }
        return mapping.get(action, "runtime")
