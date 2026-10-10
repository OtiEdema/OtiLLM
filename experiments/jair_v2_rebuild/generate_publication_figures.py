"""Regenerate publication figures from aggregated result CSVs."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def bar_metric(clean, metric, title, ylabel, out):
    systems, vals = [], []
    for r in clean:
        v = to_float(r.get(metric))
        if v is not None:
            systems.append(r["system"])
            vals.append(v)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(systems, vals)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def stress_lines(rows, metric, title, ylabel, out):
    conditions = ["noisy", "contradictory", "incomplete", "adversarial", "stale"]
    systems = sorted(set(r["system"] for r in rows))
    fig, ax = plt.subplots(figsize=(9, 5))
    for system in systems:
        lookup = {r["condition"]: to_float(r.get(metric)) for r in rows if r["system"] == system}
        y = [lookup.get(c) for c in conditions]
        if all(v is None for v in y):
            continue
        ax.plot(conditions, y, marker="o", label=system)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()

    rows = read_rows(args.summary)
    clean = [r for r in rows if r.get("condition") == "clean"]
    stress = [r for r in rows if r.get("condition") != "clean"]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for metric, title, ylabel in [
        ("token_f1", "Answer quality", "Token F1"),
        ("factuality", "Independent factuality", "Factuality"),
        ("faithfulness", "Claim-level evidence faithfulness", "Faithfulness"),
        ("unsupported_claim_rate", "Unsupported claim rate", "Rate"),
        ("coverage", "Answer coverage", "Coverage"),
        ("trace_completeness_common", "Common runtime trace completeness", "Completeness"),
    ]:
        if any(to_float(r.get(metric)) is not None for r in clean):
            bar_metric(clean, metric, title, ylabel, args.out_dir / f"clean_{metric}.png")

    if stress:
        for metric, title, ylabel in [
            ("unsupported_claim_rate", "Unsupported claims under retrieval stress", "Rate"),
            ("faithfulness", "Evidence faithfulness under retrieval stress", "Faithfulness"),
            ("coverage", "Coverage under retrieval stress", "Coverage"),
        ]:
            if any(to_float(r.get(metric)) is not None for r in stress):
                stress_lines(stress, metric, title, ylabel, args.out_dir / f"stress_{metric}.png")


if __name__ == "__main__":
    main()
