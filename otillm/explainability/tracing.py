"""Explainability and audit trace formatting."""

from otillm.types import QueryResponse


class TraceFormatter:
    """Format runtime traces into human-readable explanations."""

    def explain(self, response: QueryResponse) -> str:
        trace = response.trace
        policy = trace.policy_decision
        lines = [
            "OtiLLM Trace Report",
            "===================",
            f"Query: {trace.query}",
            f"Action: {trace.action_taken}",
            f"Confidence: {trace.confidence:.3f}",
            f"Evidence Sufficiency: {trace.evidence_sufficiency:.3f}",
            f"Memory Written: {trace.memory_written}",
        ]
        if policy is not None:
            lines.append(f"Policy Allowed: {policy.allowed}")
            lines.append(f"Policy Score: {policy.score:.3f}")
            lines.append("Policy Reasons:")
            lines.extend([f"  - {r}" for r in policy.reasons])
        if trace.retrieved_sources:
            lines.append("Retrieved Sources:")
            for src, score in zip(trace.retrieved_sources, trace.retrieved_scores):
                lines.append(f"  - {src} (score={score:.3f})")
        if trace.notes:
            lines.append("Notes:")
            lines.extend([f"  - {n}" for n in trace.notes])
        return "\n".join(lines)
