"""Paired policy validation on XSTest.

Compares OtiLLM against selected baselines on the same XSTest items using
paired binary outcomes. Reports accuracy-style policy correctness and the two
error modes separately on their relevant strata:
- safe items: false refusal;
- unsafe items: unsafe answer.

McNemar's exact binomial test is implemented without scipy so the analysis is
reproducible in the base evaluation environment. Holm adjustment is applied
within each metric family.
"""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def binom_two_sided_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # Two-sided exact McNemar under p=0.5.
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def holm(rows, p_key="mcnemar_p"):
    ordered = sorted(enumerate(rows), key=lambda x: x[1][p_key])
    m = len(ordered)
    adjusted = [None] * m
    running = 0.0
    for rank, (original_idx, row) in enumerate(ordered):
        raw = row[p_key]
        val = min(1.0, (m - rank) * raw)
        running = max(running, val)
        adjusted[original_idx] = running
    for i, row in enumerate(rows):
        row["holm_adjusted_p"] = adjusted[i]


def compare_binary(target, baseline, metric, desired_higher=True):
    ids = sorted(set(target) & set(baseline))
    tv = [int(target[i][metric]) for i in ids]
    bv = [int(baseline[i][metric]) for i in ids]

    # Discordant pairs for McNemar.
    b = sum(1 for x, y in zip(tv, bv) if x == 1 and y == 0)
    c = sum(1 for x, y in zip(tv, bv) if x == 0 and y == 1)

    tm = sum(tv) / len(tv) if tv else float("nan")
    bm = sum(bv) / len(bv) if bv else float("nan")
    diff = tm - bm
    if not desired_higher:
        # For error rates, positive improvement means target has LOWER error.
        diff = bm - tm

    return {
        "n_paired": len(ids),
        "target_mean": tm,
        "baseline_mean": bm,
        "improvement_target": diff,
        "discordant_target1_baseline0": b,
        "discordant_target0_baseline1": c,
        "mcnemar_p": binom_two_sided_exact(b, c),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--target", default="otillm_balanced")
    p.add_argument(
        "--baselines",
        nargs="+",
        default=[
            "direct_llm", "prompt_chain", "standard_rag", "strong_rag",
            "self_checking_llm", "guardrail_llm", "react_agent"
        ],
    )
    args = p.parse_args()

    systems = defaultdict(dict)
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("dataset") != "xstest" or r.get("condition", "clean") != "clean":
                continue
            systems[r["system"]][r["id"]] = r

    target = systems[args.target]
    rows = []

    families = [
        ("refusal_correct", "all", True),
        ("false_refusal", "safe", False),
        ("unsafe_answer", "unsafe", False),
    ]

    for metric, stratum, desired_higher in families:
        family_rows = []
        for baseline_name in args.baselines:
            baseline = systems[baseline_name]

            if stratum == "all":
                tsub = target
                bsub = baseline
            elif stratum == "safe":
                ids = {
                    i for i, r in target.items()
                    if float(r.get("false_refusal", 0.0)) in {0.0, 1.0}
                    and r.get("unsafe_answer") == 0.0
                    and r.get("refusal_correct") in {0.0, 1.0}
                }
                # XSTest safe rows are identified by the policy outcome encoding:
                # on safe items, unsafe_answer is always 0 and false_refusal captures error.
                # Require matching ids and use rows where at least one system exposes the
                # false-refusal decision; policy labels were already encoded upstream.
                tsub = {i: target[i] for i in ids if i in target}
                bsub = {i: baseline[i] for i in ids if i in baseline}
            else:
                # Unsafe XSTest rows: false_refusal is structurally 0 while unsafe_answer
                # captures the policy error. We identify them by whether refusing is the
                # correct action in the upstream metric encoding.
                ids = {
                    i for i, r in target.items()
                    if r.get("false_refusal") == 0.0
                    and (
                        r.get("unsafe_answer") == 1.0
                        or (
                            r.get("unsafe_answer") == 0.0
                            and r.get("coverage") == 0.0
                            and r.get("refusal_correct") == 1.0
                        )
                    )
                }
                tsub = {i: target[i] for i in ids if i in target}
                bsub = {i: baseline[i] for i in ids if i in baseline}

            result = compare_binary(tsub, bsub, metric, desired_higher)
            family_rows.append({
                "target": args.target,
                "baseline": baseline_name,
                "metric": metric,
                "stratum": stratum,
                **result,
            })

        holm(family_rows)
        rows.extend(family_rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "target", "baseline", "metric", "stratum", "n_paired",
        "target_mean", "baseline_mean", "improvement_target",
        "discordant_target1_baseline0", "discordant_target0_baseline1",
        "mcnemar_p", "holm_adjusted_p",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Saved {len(rows)} XSTest paired policy comparisons to {args.out}")


if __name__ == "__main__":
    main()
