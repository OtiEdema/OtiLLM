"""Aggregate only metrics that are actually present in raw observations."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

METRICS = [
    "exact_match", "token_f1", "faithfulness", "refusal_correct",
    "false_refusal", "unsafe_answer", "coverage", "latency_seconds",
    "llm_calls", "retrieval_calls", "input_tokens", "output_tokens", "api_cost",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    groups = defaultdict(list)
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                groups[(row["system"], row.get("condition", "clean"))].append(row)

    output = []
    for (system, condition), rows in sorted(groups.items()):
        result = {"system": system, "condition": condition, "n": len(rows)}
        for metric in METRICS:
            vals = [r.get(metric) for r in rows if isinstance(r.get(metric), (int, float))]
            result[metric] = (sum(vals) / len(vals)) if vals else ""
        output.append(result)

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0].keys()))
        writer.writeheader()
        writer.writerows(output)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
