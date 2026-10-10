"""Run deterministic retrieval-stress experiments."""

import argparse
import json
from pathlib import Path

from adapters import ExternalAdapter, OtiLLMAdapter
from backends import load_backend
from baseline_adapters import (
    DirectLLMAdapter, PromptChainAdapter, StandardRAGAdapter, StrongRAGAdapter,
    SelfCheckingAdapter, GuardrailAdapter, ReActAdapter,
)
from metrics import exact_match, faithfulness_placeholder, refusal_metrics, token_f1
from perturbations import transform

CONDITIONS = ["clean", "noisy", "contradictory", "incomplete", "adversarial", "stale"]
BASELINES = {
    "direct_llm": DirectLLMAdapter,
    "prompt_chain": PromptChainAdapter,
    "standard_rag": StandardRAGAdapter,
    "strong_rag": StrongRAGAdapter,
    "self_checking_llm": SelfCheckingAdapter,
    "guardrail_llm": GuardrailAdapter,
    "react_agent": ReActAdapter,
}


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_systems(path, backend):
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    systems = []
    for s in cfg["systems"]:
        if not s.get("enabled", False):
            continue
        if s["adapter"] == "otillm":
            systems.append(OtiLLMAdapter(s["name"], s.get("mode", "balanced"), backend))
        else:
            cls = BASELINES[s["name"]]
            systems.append(ExternalAdapter(s["name"], cls(s["name"], backend)))
    return systems


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--systems", required=True)
    p.add_argument("--backend", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    backend = load_backend(args.backend)
    systems = load_systems(args.systems, backend)
    rows = []
    for record in load_jsonl(args.manifest):
        for condition in CONDITIONS:
            evidence, perturbation_log = transform(record, condition)
            for adapter in systems:
                out = adapter.run(record, evidence)
                policy_task = record.get("metadata", {}).get("task_type") == "policy_refusal"
                metrics = {
                    "exact_match": None if policy_task else exact_match(out["answer"], record.get("references", [])),
                    "token_f1": None if policy_task else token_f1(out["answer"], record.get("references", [])),
                    "faithfulness": faithfulness_placeholder(),
                }
                metrics.update(refusal_metrics(out["action"], record.get("policy_label", "answer")))
                rows.append({
                    "id": record["id"],
                    "dataset": record["dataset"],
                    "condition": condition,
                    "backend": backend.name,
                    "perturbation_log": perturbation_log,
                    "evaluation_evidence": evidence,
                    **out,
                    **metrics,
                })

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, default=str) + "\n")
    print(f"Saved {len(rows)} stress observations to {path}")


if __name__ == "__main__":
    main()
