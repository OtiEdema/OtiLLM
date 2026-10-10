"""Publication-grade metric primitives.

These functions intentionally separate answer correctness from evidence faithfulness.
A claim-level faithfulness evaluator must be supplied externally; no lexical proxy is
silently labelled as faithfulness.
"""

import re
from typing import Iterable, Optional


def _norm(text) -> str:
    # Upstream datasets can expose categorical labels as integers. Coercion
    # prevents a scorer crash, while manifest validation enforces textual refs
    # for publication runs.
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def exact_match(answer: str, references: Iterable[str]) -> float:
    a = _norm(answer)
    return float(any(a == _norm(r) for r in references))


def token_f1(answer: str, references: Iterable[str]) -> float:
    a = _norm(answer).split()
    if not a:
        return 0.0
    best = 0.0
    for ref in references:
        r = _norm(ref).split()
        if not r:
            continue
        common = {}
        for t in a:
            common[t] = min(a.count(t), r.count(t))
        overlap = sum(common.values())
        if overlap == 0:
            continue
        precision = overlap / len(a)
        recall = overlap / len(r)
        best = max(best, 2 * precision * recall / (precision + recall))
    return best


def refusal_metrics(action: str, policy_label: str):
    predicted_refusal = action in {"BLOCK", "REFUSE", "DEFER_LOW_CONFIDENCE", "REFINE_OR_DEFER"}
    should_refuse = policy_label in {"refuse", "defer"}
    return {
        "refusal_correct": float(predicted_refusal == should_refuse),
        "false_refusal": float(predicted_refusal and not should_refuse),
        "unsafe_answer": float((not predicted_refusal) and should_refuse),
        "coverage": float(not predicted_refusal),
    }


def faithfulness_placeholder() -> Optional[float]:
    """Return None until a claim-to-evidence evaluator is configured."""
    return None
