"""Paired bootstrap confidence intervals computed from raw per-example results."""

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
    observed = sum(x - y for x, y in zip(a, b)) / n
    sims = []
    for _ in range(n_boot):
        idxs = [rng.randrange(n) for _ in range(n)]
        sims.append(sum(a[i] - b[i] for i in idxs) / n)
    return observed, percentile(sims, 0.025), percentile(sims, 0.975)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--metric", default="token_f1")
    args = p.parse_args()

    by_system = defaultdict(dict)
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("condition", "clean") != "clean":
                continue
            value = r.get(args.metric)
            if isinstance(value, (int, float)):
                by_system[r["system"]][r["id"]] = value

    systems = sorted(by_system)
    rows = []
    for i, a in enumerate(systems):
        for b in systems[i+1:]:
            ids = sorted(set(by_system[a]) & set(by_system[b]))
            if not ids:
                continue
            av = [by_system[a][x] for x in ids]
            bv = [by_system[b][x] for x in ids]
            diff, lo, hi = paired_bootstrap(av, bv)
            rows.append({
                "system_a": a,
                "system_b": b,
                "metric": args.metric,
                "n_paired": len(ids),
                "mean_difference_a_minus_b": diff,
                "bootstrap_ci_2.5": lo,
                "bootstrap_ci_97.5": hi,
            })

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else [
        "system_a","system_b","metric","n_paired",
        "mean_difference_a_minus_b","bootstrap_ci_2.5","bootstrap_ci_97.5"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
