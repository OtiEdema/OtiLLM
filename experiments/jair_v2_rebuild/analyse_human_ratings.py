"""Summarise double-adjudicated human ratings and inter-rater agreement."""

import argparse
import csv
import math
from collections import Counter
from pathlib import Path


FIELDS = [
    "correctness_yes_no_unclear",
    "factuality_yes_no_unclear",
    "faithfulness_yes_no_unclear",
    "refusal_appropriate_yes_no_unclear",
]


def cohens_kappa(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x and y]
    if not pairs:
        return float("nan")
    labels = sorted(set(x for p in pairs for x in p))
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca = Counter(x for x, _ in pairs)
    cb = Counter(y for _, y in pairs)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {r["review_id"]: r for r in csv.DictReader(f)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rater-a", type=Path, required=True)
    p.add_argument("--rater-b", type=Path, required=True)
    args = p.parse_args()

    a, b = load(args.rater_a), load(args.rater_b)
    ids = sorted(set(a) & set(b))
    print(f"paired_reviews={len(ids)}")
    for field in FIELDS:
        av = [a[i].get(field, "").strip().lower() for i in ids]
        bv = [b[i].get(field, "").strip().lower() for i in ids]
        valid = [(x, y) for x, y in zip(av, bv) if x and y]
        agreement = sum(x == y for x, y in valid) / len(valid) if valid else float("nan")
        kappa = cohens_kappa(av, bv)
        print(f"{field}: raw_agreement={agreement:.4f} kappa={kappa:.4f} n={len(valid)}")


if __name__ == "__main__":
    main()
