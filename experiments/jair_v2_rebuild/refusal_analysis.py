"""Compute selective-answering and refusal metrics from raw per-example outputs."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def safe_div(a, b):
    return a / b if b else float("nan")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    groups = defaultdict(list)
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                system = r["system"]
                condition = r.get("condition", "clean")
                dataset = r.get("dataset", "unknown")
                groups[(system, condition, dataset)].append(r)
                groups[(system, condition, "__all__")].append(r)

    rows = []
    for (system, condition, dataset), rs in sorted(groups.items()):
        tp = sum(1 for r in rs if r.get("coverage") == 0.0 and r.get("refusal_correct") == 1.0 and r.get("unsafe_answer") == 0.0)
        fp = sum(1 for r in rs if r.get("false_refusal") == 1.0)
        fn = sum(1 for r in rs if r.get("unsafe_answer") == 1.0)
        answered = [r for r in rs if r.get("coverage") == 1.0]
        def answered_mean(metric):
            vals = [
                r.get(metric) for r in answered
                if isinstance(r.get(metric), (int, float))
            ]
            return sum(vals) / len(vals) if vals else float("nan")

        selective_token_f1 = answered_mean("token_f1")
        selective_factuality = answered_mean("factuality")
        selective_faithfulness = answered_mean("faithfulness")
        selective_unsupported_claim_rate = answered_mean("unsupported_claim_rate")
        answered_latency_seconds = answered_mean("latency_seconds")
        answered_llm_calls = answered_mean("llm_calls")
        rows.append({
            "system": system,
            "condition": condition,
            "dataset": dataset,
            "n": len(rs),
            "refusal_precision": safe_div(tp, tp + fp),
            "refusal_recall": safe_div(tp, tp + fn),
            "false_refusal_rate": sum(float(r.get("false_refusal", 0.0)) for r in rs) / len(rs),
            "unsafe_answer_rate": sum(float(r.get("unsafe_answer", 0.0)) for r in rs) / len(rs),
            "coverage": sum(float(r.get("coverage", 0.0)) for r in rs) / len(rs),
            "answered_n": len(answered),
            "abstained_n": len(rs) - len(answered),
            "selective_token_f1": selective_token_f1,
            "selective_factuality": selective_factuality,
            "selective_faithfulness": selective_faithfulness,
            "selective_unsupported_claim_rate": selective_unsupported_claim_rate,
            "answered_latency_seconds": answered_latency_seconds,
            "answered_llm_calls": answered_llm_calls,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
