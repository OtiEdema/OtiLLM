from otillm.runtime.state import RuntimeState, RuntimeResult
from otillm.runtime.uncertainty import UncertaintyEngine
from otillm.runtime.utility import CognitiveUtilityOptimizer, UtilityInput
from otillm.governance import PolicyEngine
from otillm.retrieval import RetrievalReconsiderationEngine
from otillm.explainability import ERRGBuilder
from otillm.memory import GovernedMemory

class GovernedRuntime:
    """High-level OtiLLM v2.4 governed cognitive runtime.

    The runtime coordinates evidence retrieval, governance, uncertainty,
    cognitive utility optimisation, memory governance and explainability tracing.
    """

    def __init__(self):
        self.retriever = RetrievalReconsiderationEngine()
        self.policy = PolicyEngine()
        self.uncertainty = UncertaintyEngine()
        self.utility = CognitiveUtilityOptimizer()
        self.trace_builder = ERRGBuilder()
        self.memory = GovernedMemory()

    def run(self, query: str) -> RuntimeResult:
        state = RuntimeState(query=query)
        evidence = self.retriever.retrieve(query)
        governance_state = self.policy.evaluate(query, evidence)
        contradiction_density = self.retriever.contradiction_density(evidence)

        uncertainty = self.uncertainty.estimate(
            evidence=evidence,
            contradiction_density=contradiction_density,
            governance_risk=governance_state.risk,
        )

        utility = self.utility.score(
            UtilityInput(
                informational_value=0.8,
                evidence_support=max(0.0, 1.0 - uncertainty),
                helpfulness=0.8,
                hallucination_risk=uncertainty,
                governance_risk=governance_state.risk,
                operational_cost=0.05,
            )
        )

        action = self.utility.select_action(utility, uncertainty, governance_state.risk)

        if action == "reconsider_retrieval":
            evidence = self.retriever.reconsider(query, evidence)
            uncertainty = self.uncertainty.estimate(evidence, self.retriever.contradiction_density(evidence), governance_state.risk)
            action = "answer" if uncertainty < 0.70 else "clarify"

        if action == "refuse":
            answer = "The request cannot be answered safely under the current governance constraints."
        elif action == "clarify":
            answer = "The available evidence is insufficient for a reliable answer. Additional clarification or evidence is required."
        else:
            answer = self._generate_grounded_answer(query, evidence)

        self.memory.maybe_write(query=query, answer=answer, confidence=max(0.0, 1.0 - uncertainty), governance_ok=governance_state.allowed)

        trace = self.trace_builder.create_graph(
            query=query,
            evidence=evidence,
            governance_events=[governance_state.reason],
            uncertainty_score=uncertainty,
            action=action,
        )

        return RuntimeResult(
            answer=answer,
            action=action,
            confidence=max(0.0, 1.0 - uncertainty),
            evidence_used=evidence,
            trace=trace,
            metadata={
                "utility": utility,
                "uncertainty": uncertainty,
                "governance_risk": governance_state.risk,
                "contradiction_density": contradiction_density,
            },
        )

    def _generate_grounded_answer(self, query: str, evidence: list[str]) -> str:
        if not evidence:
            return "The available evidence is insufficient for a reliable answer."
        return f"Based on the governed evidence, {evidence[0]}"
