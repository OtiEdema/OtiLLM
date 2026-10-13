"""Paired selective statistical validation for governed answering.

The comparison set is defined by the target system's answered items. This avoids
comparing target answered-only metrics against baselines evaluated on a different
item population. Pairing remains at the benchmark-item level.

For each stress condition and baseline, the script:
- keeps content benchmarks only;
- selects IDs where the target answered (coverage == 1);
- pairs target and baseline on those exact IDs;
- reports target/baseline means, paired mean difference, bootstrap 95% CI,
  permutation p-value, and Holm-adjusted p-value across the comparison family.

This evaluates conditional answer quality among items the governed target chose
to answer. It must be interpreted together with coverage, not as unconditional
system accuracy.
"""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

CONTENT_DATASETS = {"truthfulqa", "fever", "hotpotqa", "natural_questions"}


def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    idx = int(round((len(xs) - 1) * q))
    return xs[max(0, min(idx, len(xs) - 1))]


def paired_bootstrap(a, b, n_boot=5000, seed=42):
    if len(a) != len(b) or not a:
        raise ValueError("Paired samples must be non-empty and equal length")
    rng = random.Random(seed)
    diffs = [x - y for x, y in zip(a, b)]
    n = len(diffs)
    observed = sum(diffs) / n
    sims = []
    for _ in range(n_boot):
        idxs = [rng.randrange(n) for _ in range(n)]
        sims.append(sum(diffs[i] for i in idxs) / n)
    return observed, percentile(sims, 0.025), percentile(sims, 0.975)


def paired_permutation_pvalue(a, b, n_perm=10000, seed=42):
    if len(a) != len(b) or not a:
        raise ValueError("Paired samples must be non-empty and equal length")
    rng = random.Random(seed)
    diffs = [x - y for x, y in zip(a, b)]
    obs = abs(sum(diffs) / len(diffs))
    ge = 0
    for _ in range(n_perm):
        sim = sum((d if rng.random() < 0.5 else -d) for d in diffs) / len(diffs)
        if abs(sim) >= obs:
            ge += 1
    return (ge + 1) / (n_perm + 1)


def holm_adjust(rows, p_key="paired_permutation_p"):
    ordered = sorted(enumerate(rows), key=lambda x: x[1][p_key])
    m = len(ordered)
    adjusted = [None] * m
    running = 0.0
    for rank, (original_idx, row) in enumerate(ordered):
        raw_p = row[p_key]
        holm = min(1.0, (m - rank) * raw_p)
        running = max(running, holm)
        adjusted[original_idx] = running
    for i, row in enumerate(rows):
        row["holm_adjusted_p"] = adjusted[i] if adjusted else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--target", default="otillm_balanced")
    p.add_argument(
        "--baselines",
        nargs="+",
        default=["standard_rag", "strong_rag", "react_agent"],
    )
    p.add_argument("--metric", default="faithfulness")
    p.add_argument(
        "--conditions",
        nargs="+",
        default=["noisy", "contradictory", "incomplete", "adversarial", "stale"],
    )
    p.add_argument("--bootstrap", type=int, default=5000)
    p.add_argument("--permutations", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    # condition -> system -> id -> row
    by_condition = defaultdict(lambda: defaultdict(dict))
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("dataset") not in CONTENT_DATASETS:
                continue
            condition = r.get("condition", "clean")
            if condition not in args.conditions:
                continue
            system = r.get("system")
            if system not in {args.target, *args.baselines}:
                continue
            by_condition[condition][system][r["id"]] = r

    rows = []
    for condition in args.conditions:
        systems = by_condition.get(condition, {})
        target_rows = systems.get(args.target, {})
        answered_ids = {
            rid
            for rid, r in target_rows.items()
            if float(r.get("coverage", 0.0)) == 1.0
            and isinstance(r.get(args.metric), (int, float))
        }

        for baseline in args.baselines:
            baseline_rows = systems.get(baseline, {})
            ids = sorted(
                rid
                for rid in answered_ids
                if rid in baseline_rows
                and isinstance(baseline_rows[rid].get(args.metric), (int, float))
            )
            if not ids:
                continue

            tv = [target_rows[rid][args.metric] for rid in ids]
            bv = [baseline_rows[rid][args.metric] for rid in ids]
            diff, lo, hi = paired_bootstrap(
                tv, bv, n_boot=args.bootstrap, seed=args.seed
            )
            pvalue = paired_permutation_pvalue(
                tv, bv, n_perm=args.permutations, seed=args.seed
            )

            rows.append({
                "target": args.target,
                "baseline": baseline,
                "condition": condition,
                "metric": args.metric,
                "target_total_items": len(target_rows),
                "target_answered_items": len(answered_ids),
                "n_paired": len(ids),
                "target_coverage": (
                    len(answered_ids) / len(target_rows) if target_rows else float("nan")
                ),
                "target_mean": sum(tv) / len(tv),
                "baseline_mean_on_target_answered_subset": sum(bv) / len(bv),
                "mean_difference_target_minus_baseline": diff,
                "bootstrap_ci_2.5": lo,
                "bootstrap_ci_97.5": hi,
                "paired_permutation_p": pvalue,
            })

    holm_adjust(rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "target", "baseline", "condition", "metric",
        "target_total_items", "target_answered_items", "n_paired",
        "target_coverage", "target_mean",
        "baseline_mean_on_target_answered_subset",
        "mean_difference_target_minus_baseline",
        "bootstrap_ci_2.5", "bootstrap_ci_97.5",
        "paired_permutation_p", "holm_adjusted_p",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Saved {len(rows)} selective paired comparisons to {args.out}")


if __name__ == "__main__":
    main()
