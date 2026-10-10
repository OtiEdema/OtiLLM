"""Common observable trace schema applied to every evaluated system.

This avoids defining trace completeness in terms of OtiLLM-specific fields.
"""

COMMON_TRACE_FIELDS = (
    "query_received",
    "retrieval_attempted",
    "evidence_selected",
    "model_invoked",
    "policy_decision_recorded",
    "confidence_recorded",
    "action_recorded",
    "final_output_recorded",
)


def common_trace_completeness(trace: dict) -> float:
    if not COMMON_TRACE_FIELDS:
        return 0.0
    observed = sum(bool(trace.get(field, False)) for field in COMMON_TRACE_FIELDS)
    return observed / len(COMMON_TRACE_FIELDS)
