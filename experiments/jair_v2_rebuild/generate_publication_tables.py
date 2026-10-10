"""Generate manuscript-ready CSV tables from aggregated raw results."""

import argparse
import csv
from pathlib import Path


DISPLAY = {
    "exact_match": "Exact match",
    "token_f1": "Token F1",
    "factuality": "Factuality",
    "faithfulness": "Faithfulness",
    "unsupported_claim_rate": "Unsupported claim rate",
    "refusal_correct": "Refusal correctness",
    "false_refusal": "False refusal rate",
    "unsafe_answer": "Unsafe answer rate",
    "coverage": "Coverage",
    "trace_completeness_common": "Common trace completeness",
    "latency_seconds": "Latency (s)",
    "llm_calls": "LLM calls",
    "retrieval_calls": "Retrieval calls",
    "input_tokens": "Input tokens",
    "output_tokens": "Output tokens",
}


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()

    rows = read_csv(args.summary)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    clean = [r for r in rows if r.get("condition") == "clean"]
    metrics = [m for m in DISPLAY if any(r.get(m, "") not in ("", None) for r in clean)]

    table1 = args.out_dir / "table_primary_clean.csv"
    with table1.open("w", newline="", encoding="utf-8") as f:
        fields = ["system", "n"] + metrics
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in clean:
            w.writerow({k: r.get(k, "") for k in fields})

    stress = [r for r in rows if r.get("condition") != "clean"]
    table2 = args.out_dir / "table_stress.csv"
    with table2.open("w", newline="", encoding="utf-8") as f:
        fields = ["system", "condition", "n", "factuality", "faithfulness",
                  "unsupported_claim_rate", "unsafe_answer", "coverage",
                  "trace_completeness_common", "latency_seconds"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in stress:
            w.writerow({k: r.get(k, "") for k in fields})

    print(table1)
    print(table2)


if __name__ == "__main__":
    main()
