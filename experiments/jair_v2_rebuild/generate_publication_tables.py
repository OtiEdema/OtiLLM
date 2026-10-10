"""Generate manuscript-ready CSV tables from aggregated results."""

import argparse
import csv
from pathlib import Path


CONTENT_DATASETS = {"truthfulqa", "fever", "hotpotqa", "natural_questions"}


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()

    rows = read_csv(args.summary)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Per-dataset content performance, keeping benchmark identities visible.
    content_clean = [
        r for r in rows
        if r.get("condition") == "clean" and r.get("dataset") in CONTENT_DATASETS
    ]
    write(
        args.out_dir / "table_content_by_dataset.csv",
        content_clean,
        [
            "system","dataset","n","exact_match","token_f1","factuality",
            "faithfulness","unsupported_claim_rate","coverage",
            "trace_completeness_common","latency_seconds","llm_calls",
            "retrieval_calls","input_tokens","output_tokens"
        ],
    )

    # XSTest is reported separately; it is not averaged into QA correctness.
    policy = [
        r for r in rows
        if r.get("condition") == "clean" and r.get("dataset") == "xstest"
    ]
    write(
        args.out_dir / "table_policy_xstest.csv",
        policy,
        [
            "system","n","refusal_correct","false_refusal","unsafe_answer",
            "coverage","trace_completeness_common","latency_seconds","llm_calls"
        ],
    )

    # Retrieval stress: only content benchmarks are present by design.
    stress = [
        r for r in rows
        if r.get("condition") != "clean" and r.get("dataset") in CONTENT_DATASETS
    ]
    write(
        args.out_dir / "table_retrieval_stress_by_dataset.csv",
        stress,
        [
            "system","dataset","condition","n","factuality","faithfulness",
            "unsupported_claim_rate","unsafe_answer","coverage",
            "trace_completeness_common","latency_seconds"
        ],
    )

    # Overall row is useful for cost/trace only. Content-quality interpretation
    # should rely on per-dataset or explicitly macro-averaged analyses.
    overall = [
        r for r in rows
        if r.get("condition") == "clean" and r.get("dataset") == "__all__"
    ]
    write(
        args.out_dir / "table_overall_operations.csv",
        overall,
        [
            "system","n","trace_completeness_common","latency_seconds",
            "llm_calls","retrieval_calls","input_tokens","output_tokens"
        ],
    )

    for pth in sorted(args.out_dir.glob("table_*.csv")):
        print(pth)


if __name__ == "__main__":
    main()
