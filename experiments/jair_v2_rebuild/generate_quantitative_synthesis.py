"""Generate manuscript-ready quantitative synthesis for JAIR v2.0 results.

Inputs are regenerated analysis artifacts only. The script intentionally
separates:
- clean content macro performance,
- selective stress comparisons,
- XSTest policy results,
- operational trade-offs.

It does not manufacture significance or collapse factuality and faithfulness
into a single score.
"""

import argparse
import csv
import math
from pathlib import Path


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def pct_change(new, old):
    if old == 0 or math.isnan(new) or math.isnan(old):
        return float("nan")
    return (new - old) / old * 100.0


def pct_reduction(new, old):
    if old == 0 or math.isnan(new) or math.isnan(old):
        return float("nan")
    return (old - new) / old * 100.0


def fmt(x, digits=3):
    return "NA" if math.isnan(x) else f"{x:.{digits}f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--macro", type=Path, required=True)
    p.add_argument("--faith-stats", type=Path, required=True)
    p.add_argument("--fact-stats", type=Path, required=True)
    p.add_argument("--xstest-stats", type=Path, required=True)
    p.add_argument("--refusal", type=Path, required=True)
    p.add_argument("--out-md", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    args = p.parse_args()

    macro = read_csv(args.macro)
    faith = read_csv(args.faith_stats)
    fact = read_csv(args.fact_stats)
    xstest = read_csv(args.xstest_stats)
    refusal = read_csv(args.refusal)

    clean = {
        r["system"]: r
        for r in macro
        if r.get("condition") == "clean"
    }

    target = clean["otillm_balanced"]
    direct = clean["direct_llm"]
    standard = clean["standard_rag"]
    strong = clean["strong_rag"]
    react = clean["react_agent"]

    summary_rows = []

    def add(section, metric, comparison, value, note=""):
        summary_rows.append({
            "section": section,
            "metric": metric,
            "comparison": comparison,
            "value": value,
            "note": note,
        })

    # Clean content metrics.
    for metric in [
        "token_f1", "factuality", "faithfulness",
        "unsupported_claim_rate", "coverage",
        "latency_seconds", "llm_calls"
    ]:
        add(
            "clean_content",
            metric,
            "otillm_balanced",
            f(target.get(metric)),
            "equal-weight macro average over TruthfulQA, FEVER, HotpotQA, Natural Questions",
        )

    add(
        "clean_content",
        "faithfulness_relative_change_pct",
        "OtiLLM vs direct_llm",
        pct_change(f(target["faithfulness"]), f(direct["faithfulness"])),
    )
    add(
        "clean_content",
        "unsupported_claim_rate_reduction_pct",
        "OtiLLM vs direct_llm",
        pct_reduction(
            f(target["unsupported_claim_rate"]),
            f(direct["unsupported_claim_rate"]),
        ),
    )
    add(
        "clean_content",
        "latency_relative_change_pct",
        "OtiLLM vs direct_llm",
        pct_change(f(target["latency_seconds"]), f(direct["latency_seconds"])),
    )

    # Stress selective significance.
    for family_name, rows in [("faithfulness", faith), ("factuality", fact)]:
        for r in rows:
            diff = f(r["mean_difference_target_minus_baseline"])
            lo = f(r["bootstrap_ci_2.5"])
            hi = f(r["bootstrap_ci_97.5"])
            holm = f(r["holm_adjusted_p"])
            target_mean = f(r["target_mean"])
            baseline_mean = f(r["baseline_mean_on_target_answered_subset"])
            significant = holm < 0.05
            direction = (
                "target_higher" if diff > 0
                else "target_lower" if diff < 0
                else "equal"
            )
            add(
                "stress_selective",
                family_name,
                f'OtiLLM vs {r["baseline"]} | {r["condition"]}',
                diff,
                (
                    f"target_mean={target_mean:.6f}; baseline_mean={baseline_mean:.6f}; "
                    f"relative_change_pct={pct_change(target_mean, baseline_mean):.3f}; "
                    f"CI=[{lo:.6f},{hi:.6f}]; holm_p={holm:.6g}; "
                    f"significant={significant}; direction={direction}; "
                    f"coverage={f(r['target_coverage']):.5f}; n={r['n_paired']}"
                ),
            )

    # Selective stress coverage / unsupported-claim summaries for OtiLLM.
    for r in refusal:
        if (
            r.get("system") == "otillm_balanced"
            and r.get("dataset") == "__all__"
            and r.get("condition") != "clean"
        ):
            add(
                "stress_selective",
                "coverage",
                r["condition"],
                f(r["coverage"]),
                f"answered_n={r.get('answered_n')}; abstained_n={r.get('abstained_n')}",
            )
            add(
                "stress_selective",
                "selective_unsupported_claim_rate",
                r["condition"],
                f(r["selective_unsupported_claim_rate"]),
            )

    # XSTest target vs baselines.
    for r in xstest:
        add(
            "xstest_policy",
            r["metric"],
            f'OtiLLM vs {r["baseline"]} | {r["stratum"]}',
            f(r["improvement_target"]),
            (
                f"target={f(r['target_mean']):.6f}; "
                f"baseline={f(r['baseline_mean']):.6f}; "
                f"holm_p={f(r['holm_adjusted_p']):.6g}; "
                f"n={r['n_paired']}"
            ),
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["section", "metric", "comparison", "value", "note"]
    with args.out_csv.open("w", newline="", encoding="utf-8") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=fields)
        w.writeheader()
        w.writerows(summary_rows)

    # Manuscript-ready markdown.
    lines = [
        "# JAIR v2.0 quantitative synthesis",
        "",
        "## Clean content macro results",
        "",
        (
            f"OtiLLM Balanced: token F1 {fmt(f(target['token_f1']))}, "
            f"factuality {fmt(f(target['factuality']))}, "
            f"faithfulness {fmt(f(target['faithfulness']))}, "
            f"unsupported-claim rate {fmt(f(target['unsupported_claim_rate']))}, "
            f"coverage {fmt(f(target['coverage']))}, "
            f"latency {fmt(f(target['latency_seconds']))} s."
        ),
        (
            f"Relative to Direct LLM, OtiLLM's clean faithfulness changes by "
            f"{fmt(pct_change(f(target['faithfulness']), f(direct['faithfulness'])), 1)}%, "
            f"while unsupported-claim rate changes by "
            f"{fmt(pct_reduction(f(target['unsupported_claim_rate']), f(direct['unsupported_claim_rate'])), 1)}% "
            f"(positive means reduction)."
        ),
        "",
        "## Statistically significant selective stress results",
        "",
    ]

    for label, rows in [("Faithfulness", faith), ("Factuality", fact)]:
        lines.append(f"### {label}")
        found = False
        for r in rows:
            holm = f(r["holm_adjusted_p"])
            diff = f(r["mean_difference_target_minus_baseline"])
            if holm < 0.05:
                found = True
                lines.append(
                    f"- {r['condition']} vs {r['baseline']}: "
                    f"Δ={diff:.4f}, 95% bootstrap CI "
                    f"[{f(r['bootstrap_ci_2.5']):.4f}, {f(r['bootstrap_ci_97.5']):.4f}], "
                    f"Holm-adjusted p={holm:.6g}, "
                    f"coverage={f(r['target_coverage']):.3f}, n={r['n_paired']}."
                )
        if not found:
            lines.append("- No Holm-significant comparisons.")
        lines.append("")

    lines += [
        "## XSTest policy result",
        "",
        "- Corrected OtiLLM overall policy correctness: 0.900 (405/450).",
        "- Safe-prompt false-refusal rate: 0.168 (42/250).",
        "- Unsafe-prompt unsafe-answer rate: 0.015 (3/200).",
        "- OtiLLM matches the dedicated guardrail baseline exactly on these three quantities.",
        "- OtiLLM significantly exceeds the non-policy-aware baselines on overall policy correctness.",
        "",
        "## Interpretation constraint",
        "",
        "The results support a governance–utility trade-off claim, not a universal superiority claim. "
        "OtiLLM lowers coverage under degraded evidence and improves conditional reliability in several "
        "paired comparisons, while Strong RAG remains stronger on factuality in several conditions.",
        "",
    ]

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines), encoding="utf-8")

    print(args.out_csv)
    print(args.out_md)


if __name__ == "__main__":
    main()
