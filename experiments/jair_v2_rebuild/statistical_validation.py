"""Paired statistical validation from raw per-example results.

No values are hard-coded. The benchmark item is the paired unit.
"""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


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
    n = len(a)
    diffs = [x - y for x, y in zip(a, b)]
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--metric", default="token_f1")
    p.add_argument("--condition", default="clean")
    p.add_argument("--bootstrap", type=int, default=5000)
    p.add_argument("--permutations", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    by_system = defaultdict(dict)
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("condition", "clean") != args.condition:
                continue
            value = r.get(args.metric)
            if isinstance(value, (int, float)):
                by_system[r["system"]][r["id"]] = value

    systems = sorted(by_system)
    rows = []
    for i, a in enumerate(systems):
        for b in systems[i + 1:]:
            ids = sorted(set(by_system[a]) & set(by_system[b]))
            if not ids:
                continue
            av = [by_system[a][x] for x in ids]
            bv = [by_system[b][x] for x in ids]
            diff, lo, hi = paired_bootstrap(av, bv, args.bootstrap, args.seed)
            pvalue = paired_permutation_pvalue(av, bv, args.permutations, args.seed)
            rows.append({
                "system_a": a,
                "system_b": b,
                "condition": args.condition,
                "metric": args.metric,
                "n_paired": len(ids),
                "mean_difference_a_minus_b": diff,
                "bootstrap_ci_2.5": lo,
                "bootstrap_ci_97.5": hi,
                "paired_permutation_p": pvalue,
            })

    # Holm adjustment across the family of pairwise comparisons for this
    # metric/condition.
    ordered = sorted(enumerate(rows), key=lambda x: x[1]["paired_permutation_p"])
    m = len(ordered)
    running = 0.0
    adjusted = [None] * m
    for rank, (original_idx, row) in enumerate(ordered):
        raw_p = row["paired_permutation_p"]
        holm = min(1.0, (m - rank) * raw_p)
        running = max(running, holm)
        adjusted[original_idx] = running
    for i, row in enumerate(rows):
        row["holm_adjusted_p"] = adjusted[i] if adjusted else None

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "system_a","system_b","condition","metric","n_paired",
        "mean_difference_a_minus_b","bootstrap_ci_2.5",
        "bootstrap_ci_97.5","paired_permutation_p","holm_adjusted_p"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} pairwise comparisons to {path}")


if __name__ == "__main__":
    main()
