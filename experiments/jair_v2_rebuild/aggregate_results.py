"""Aggregate raw observations without mixing policy and content tasks."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

METRICS = [
    "exact_match", "token_f1", "factuality", "faithfulness",
    "unsupported_claim_rate", "refusal_correct", "false_refusal",
    "unsafe_answer", "coverage", "latency_seconds",
    "trace_completeness_common", "llm_calls", "retrieval_calls",
    "input_tokens", "output_tokens", "api_cost",
]


def summarise(rows):
    result = {"n": len(rows)}
    for metric in METRICS:
        vals = [r.get(metric) for r in rows if isinstance(r.get(metric), (int, float))]
        result[metric] = (sum(vals) / len(vals)) if vals else ""
        result[f"{metric}_n"] = len(vals)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    raw = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw.append(json.loads(line))

    groups = defaultdict(list)
    for row in raw:
        system = row["system"]
        condition = row.get("condition", "clean")
        dataset = row.get("dataset", "unknown")
        groups[(system, condition, dataset)].append(row)
        groups[(system, condition, "__all__")].append(row)

    output = []
    for (system, condition, dataset), rows in sorted(groups.items()):
        output.append({
            "system": system,
            "condition": condition,
            "dataset": dataset,
            **summarise(rows),
        })

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(output[0].keys()) if output else ["system","condition","dataset","n"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
    print(f"Saved {len(output)} aggregate rows to {path}")


if __name__ == "__main__":
    main()
