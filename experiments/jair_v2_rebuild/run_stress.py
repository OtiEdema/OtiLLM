"""Run deterministic retrieval-stress experiments."""

import argparse
import json
from pathlib import Path

from adapters import ExternalAdapter, OtiLLMAdapter
from metrics import exact_match, faithfulness_placeholder, refusal_metrics, token_f1
from perturbations import transform

CONDITIONS = ["clean", "noisy", "contradictory", "incomplete", "adversarial", "stale"]


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_systems(path):
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    systems = []
    for s in cfg["systems"]:
        if not s.get("enabled", False):
            continue
        systems.append(
            OtiLLMAdapter(s["name"], s.get("mode", "balanced"))
            if s["adapter"] == "otillm" else ExternalAdapter(s["name"])
        )
    return systems


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--systems", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    rows = []
    systems = load_systems(args.systems)
    for record in load_jsonl(args.manifest):
        for condition in CONDITIONS:
            evidence, perturbation_log = transform(record, condition)
            for adapter in systems:
                out = adapter.run(record, evidence)
                metrics = {
                    "exact_match": exact_match(out["answer"], record.get("references", [])),
                    "token_f1": token_f1(out["answer"], record.get("references", [])),
                    "faithfulness": faithfulness_placeholder(),
                }
                metrics.update(refusal_metrics(out["action"], record.get("policy_label", "answer")))
                rows.append({
                    "id": record["id"],
                    "dataset": record["dataset"],
                    "condition": condition,
                    "perturbation_log": perturbation_log,
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
