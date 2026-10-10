"""Compute macro-averages across the four content benchmarks.

Each benchmark receives equal weight, preventing a benchmark with more eligible
rows from dominating the headline aggregate. XSTest remains a separate policy
benchmark and is never folded into content quality.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

CONTENT_DATASETS = {"truthfulqa", "fever", "hotpotqa", "natural_questions"}
METRICS = [
    "exact_match","token_f1","factuality","faithfulness",
    "unsupported_claim_rate","coverage","trace_completeness_common",
    "latency_seconds","llm_calls","retrieval_calls","input_tokens","output_tokens"
]


def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args=p.parse_args()

    with args.summary.open("r", encoding="utf-8-sig", newline="") as f:
        rows=list(csv.DictReader(f))

    grouped=defaultdict(list)
    for r in rows:
        if r.get("dataset") in CONTENT_DATASETS:
            grouped[(r["system"], r["condition"])].append(r)

    out=[]
    for (system,condition), rs in sorted(grouped.items()):
        row={"system":system,"condition":condition,"datasets":len(rs)}
        for m in METRICS:
            vals=[to_float(r.get(m)) for r in rs]
            vals=[v for v in vals if v is not None]
            row[m]=sum(vals)/len(vals) if vals else ""
        out.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields=["system","condition","datasets"]+METRICS
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(out)
    print(f"Saved {len(out)} macro-average rows to {args.out}")


if __name__=="__main__":
    main()
