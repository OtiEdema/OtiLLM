"""Generate final JAIR publication tables and figures from corrected artefacts.

This script produces the manuscript-facing assets defined in
INTEGRATED_MANUSCRIPT_DRAFT.md. It never reads legacy results and it keeps
coverage visible alongside selective metrics.

Expected inputs:
- corrected aggregate summary
- corrected content macro averages
- paired selective faithfulness statistics
- paired selective factuality statistics
- corrected XSTest paired policy statistics
- corrected refusal/selective analysis

Outputs:
- six manuscript CSV tables
- five publication PNG/PDF figures
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


CONTENT = ["truthfulqa", "fever", "hotpotqa", "natural_questions"]
STRESS = ["noisy", "contradictory", "incomplete", "adversarial", "stale"]
SYSTEM_LABELS = {
    "direct_llm": "Direct LLM",
    "prompt_chain": "Prompt Chain",
    "standard_rag": "Standard RAG",
    "strong_rag": "Strong RAG",
    "self_checking_llm": "Self-Checking LLM",
    "guardrail_llm": "Guardrail LLM",
    "react_agent": "ReAct",
    "otillm_balanced": "OtiLLM Balanced",
}


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def save(fig, base):
    fig.tight_layout()
    fig.savefig(str(base) + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(str(base) + ".pdf", bbox_inches="tight")
    plt.close(fig)


def table_systems(out_dir):
    rows = [
        {"system":"Direct LLM","model_calls":"1","retrieval":"No","policy_gate":"No","selective_execution":"No","clean":"Yes","stress":"No"},
        {"system":"Prompt Chain","model_calls":"2","retrieval":"No","policy_gate":"No","selective_execution":"No","clean":"Yes","stress":"No"},
        {"system":"Standard RAG","model_calls":"1","retrieval":"Yes","policy_gate":"No","selective_execution":"No controller gate (100% stress coverage)","clean":"Yes","stress":"Yes"},
        {"system":"Strong RAG","model_calls":"1","retrieval":"Yes + reranking","policy_gate":"No","selective_execution":"No controller gate (100% stress coverage)","clean":"Yes","stress":"Yes"},
        {"system":"Self-Checking LLM","model_calls":"2","retrieval":"No","policy_gate":"No","selective_execution":"No","clean":"Yes","stress":"No"},
        {"system":"Guardrail LLM","model_calls":"1-2","retrieval":"No","policy_gate":"Yes","selective_execution":"Policy refusal","clean":"Yes","stress":"No"},
        {"system":"ReAct","model_calls":"2","retrieval":"Yes","policy_gate":"No","selective_execution":"No controller gate (100% stress coverage)","clean":"Yes","stress":"Yes"},
        {"system":"OtiLLM Balanced","model_calls":"0-2","retrieval":"Yes for content","policy_gate":"Yes","selective_execution":"Evidence/confidence defer + policy refusal","clean":"Yes","stress":"Yes"},
    ]
    fields = ["system","model_calls","retrieval","policy_gate","selective_execution","clean","stress"]
    write_csv(out_dir / "Table_1_systems_and_controls.csv", rows, fields)


def table_benchmarks(out_dir):
    rows = [
        {"benchmark":"TruthfulQA","items":200,"role":"Content QA","benchmark_native_evidence":"No","clean":"Yes","stress":"Yes","macro_content":"Yes"},
        {"benchmark":"FEVER","items":200,"role":"Fact verification/content","benchmark_native_evidence":"Yes","clean":"Yes","stress":"Yes","macro_content":"Yes"},
        {"benchmark":"HotpotQA","items":200,"role":"Multi-hop QA","benchmark_native_evidence":"Yes","clean":"Yes","stress":"Yes","macro_content":"Yes"},
        {"benchmark":"Natural Questions","items":200,"role":"Open-domain QA","benchmark_native_evidence":"Yes","clean":"Yes","stress":"Yes","macro_content":"Yes"},
        {"benchmark":"XSTest","items":450,"role":"Policy/refusal calibration","benchmark_native_evidence":"Not required","clean":"Yes","stress":"No","macro_content":"No"},
    ]
    fields = ["benchmark","items","role","benchmark_native_evidence","clean","stress","macro_content"]
    write_csv(out_dir / "Table_2_benchmark_composition.csv", rows, fields)


def table_clean_macro(macro, out_dir):
    rows = []
    for r in macro:
        if r.get("condition") != "clean":
            continue
        rows.append({
            "system": SYSTEM_LABELS.get(r["system"], r["system"]),
            "token_f1": r.get("token_f1",""),
            "reference_factuality_nli": r.get("factuality",""),
            "evidence_faithfulness_nli": r.get("faithfulness",""),
            "unsupported_claim_rate": r.get("unsupported_claim_rate",""),
            "coverage": r.get("coverage",""),
            "latency_seconds": r.get("latency_seconds",""),
            "llm_calls": r.get("llm_calls",""),
        })
    fields = [
        "system","token_f1","reference_factuality_nli",
        "evidence_faithfulness_nli","unsupported_claim_rate","coverage",
        "latency_seconds","llm_calls"
    ]
    write_csv(out_dir / "Table_3_clean_content_macro.csv", rows, fields)


def table_selective(rows, name, out_dir):
    formatted = []
    for r in rows:
        formatted.append({
            "condition": r["condition"],
            "baseline": SYSTEM_LABELS.get(r["baseline"], r["baseline"]),
            "n_paired": r["n_paired"],
            "otillm_coverage": r["target_coverage"],
            "otillm_mean": r["target_mean"],
            "baseline_mean_on_same_items": r["baseline_mean_on_target_answered_subset"],
            "paired_difference": r["mean_difference_target_minus_baseline"],
            "ci_2.5": r["bootstrap_ci_2.5"],
            "ci_97.5": r["bootstrap_ci_97.5"],
            "holm_adjusted_p": r["holm_adjusted_p"],
            "significant_0.05": "Yes" if (
                num(r["holm_adjusted_p"]) is not None
                and num(r["holm_adjusted_p"]) < 0.05
            ) else "No",
        })
    fields = [
        "condition","baseline","n_paired","otillm_coverage","otillm_mean",
        "baseline_mean_on_same_items","paired_difference","ci_2.5","ci_97.5",
        "holm_adjusted_p","significant_0.05"
    ]
    write_csv(out_dir / name, formatted, fields)


def table_xstest(rows, out_dir):
    formatted = []
    for r in rows:
        formatted.append({
            "metric": r["metric"],
            "stratum": r["stratum"],
            "baseline": SYSTEM_LABELS.get(r["baseline"], r["baseline"]),
            "n_paired": r["n_paired"],
            "otillm_mean": r["target_mean"],
            "baseline_mean": r["baseline_mean"],
            "improvement_target": r["improvement_target"],
            "mcnemar_p": r["mcnemar_p"],
            "holm_adjusted_p": r["holm_adjusted_p"],
        })
    fields = [
        "metric","stratum","baseline","n_paired","otillm_mean","baseline_mean",
        "improvement_target","mcnemar_p","holm_adjusted_p"
    ]
    write_csv(out_dir / "Table_6_xstest_policy.csv", formatted, fields)


def figure_architecture(out_dir):
    """Draw controller branches without routing failure paths through generation."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x, y, w, h, label):
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, linewidth=1.3))
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=10)

    def edge(points, label=None, label_at=None):
        xs, ys = zip(*points)
        ax.plot(xs[:-1], ys[:-1], color="black", linewidth=1.1)
        ax.annotate("", xy=points[-1], xytext=points[-2],
                    arrowprops=dict(arrowstyle="->", linewidth=1.1))
        if label:
            ax.text(*label_at, label, fontsize=9, ha="center", va="center",
                    bbox=dict(facecolor="white", edgecolor="none", pad=1))

    box(.04, .85, .17, .08, "Query")
    box(.32, .85, .23, .08, "Static policy")
    box(.76, .85, .20, .08, "Block")
    box(.06, .65, .25, .10, "Content task:\nretrieve top five")
    box(.06, .46, .25, .10, "Evidence sufficient?\nscore >= 0.40")
    box(.06, .27, .25, .10, "Confidence gate*\nscore >= 0.55")
    box(.53, .65, .26, .10, "Policy-only task:\nsemantic classifier")
    box(.82, .65, .15, .10, "Refuse")
    box(.42, .46, .15, .10, "Defer")
    box(.53, .27, .26, .10, "Execute generation")
    box(.53, .10, .26, .09, "Content only:\nmemory-write gate")
    edge([(.21,.89),(.32,.89)])
    edge([(.55,.89),(.76,.89)], "Blocked", (.655,.91))
    edge([(.38,.85),(.38,.80),(.185,.80),(.185,.75)], "Permitted", (.27,.815))
    edge([(.49,.85),(.49,.80),(.66,.80),(.66,.75)])
    edge([(.185,.65),(.185,.56)])
    edge([(.31,.51),(.42,.51)], "No", (.365,.53))
    edge([(.185,.46),(.185,.37)], "Yes", (.21,.415))
    edge([(.31,.32),(.53,.32)], "Pass", (.42,.34))
    edge([(.28,.37),(.28,.41),(.495,.41),(.495,.46)], "Fail*", (.40,.43))
    edge([(.79,.70),(.82,.70)], "Unsafe", (.87,.78))
    edge([(.66,.65),(.66,.37)], "Safe", (.69,.50))
    edge([(.66,.27),(.66,.19)])
    ax.text(.5,.98,"Implemented OtiLLM publication controller",ha="center",fontsize=14)
    ax.text(.04,.16,"*Confidence cannot independently defer\na permitted content query at these defaults.\nAll paths record a runtime trace.",
            ha="left",va="center",fontsize=9)
    ax.text(.5,.035,"Not evaluated: adaptive re-retrieval, learned control and longitudinal memory.",
            ha="center",fontsize=9)
    save(fig,out_dir/"Figure_1_governed_runtime_architecture")

def figure_pipeline(out_dir):
    """Show clean and stress generation as parallel branches."""
    fig, ax = plt.subplots(figsize=(12, 5.0))
    ax.axis("off")

    def box(x,y,w,h,label):
        ax.add_patch(plt.Rectangle((x,y),w,h,fill=False,linewidth=1.3))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=9)

    box(0.03,0.45,0.12,0.18,"Frozen\nmanifest")
    box(0.22,0.67,0.13,0.18,"Clean\ngeneration")
    box(0.22,0.23,0.13,0.18,"Stress\ngeneration")
    box(0.42,0.45,0.15,0.18,"Shard merge +\nintegrity checks")
    box(0.63,0.45,0.13,0.18,"Independent\nNLI scoring")
    box(0.81,0.45,0.15,0.18,"Aggregate + paired\nstatistics + assets")

    arrows=[
        ((0.15,0.54),(0.22,0.76)),
        ((0.15,0.54),(0.22,0.32)),
        ((0.35,0.76),(0.42,0.56)),
        ((0.35,0.32),(0.42,0.52)),
        ((0.57,0.54),(0.63,0.54)),
        ((0.76,0.54),(0.81,0.54)),
    ]
    for a,b in arrows:
        ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="->",linewidth=1.1))

    ax.text(0.5,0.94,"Deterministic publication evaluation pipeline",ha="center",fontsize=14)
    ax.text(
        0.5,0.08,
        "Persistent Google Drive checkpoints • resumable deterministic shards • frozen checksums • final corrected dataset: 26,000 rows",
        ha="center",fontsize=8.5
    )
    save(fig,out_dir/"Figure_2_reproducibility_pipeline")

def selective_tradeoff(rows, metric_name, out_base, out_dir):
    """Plot matched-subset metric values while keeping OtiLLM coverage visible.

    Baseline y-values are evaluated on the exact OtiLLM-answered items. Baseline
    coverage is not placed on the x-axis because that would mix conditional
    matched-subset means with their unconditional 100% stress coverage.
    """
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    positions = list(range(len(STRESS)))
    systems = ["standard_rag","strong_rag","react_agent"]
    markers = {"standard_rag":"s","strong_rag":"^","react_agent":"D"}

    target = {}
    baseline = {s:{} for s in systems}
    coverage = {}
    for r in rows:
        cond=r["condition"]
        target.setdefault(cond,num(r["target_mean"]))
        coverage.setdefault(cond,num(r["target_coverage"]))
        if r["baseline"] in baseline:
            baseline[r["baseline"]][cond]=num(r["baseline_mean_on_target_answered_subset"])

    ax.plot(
        positions,[target.get(c) for c in STRESS],
        marker="o",linewidth=1.8,label="OtiLLM Balanced"
    )
    for system in systems:
        ax.plot(
            positions,[baseline[system].get(c) for c in STRESS],
            marker=markers[system],linewidth=1.2,label=SYSTEM_LABELS[system]
        )

    ax.set_xticks(positions, STRESS, rotation=20)
    ax.set_ylabel(metric_name)
    ax.set_xlabel("Retrieval-stress condition")
    ax.set_title(f"Matched-subset {metric_name.lower()} with OtiLLM coverage")
    ax.grid(True,axis="y",alpha=0.25)

    ax2=ax.twinx()
    ax2.plot(
        positions,[coverage.get(c) for c in STRESS],
        linestyle="--",marker="x",linewidth=1.1,label="OtiLLM coverage"
    )
    ax2.set_ylabel("OtiLLM execution coverage")
    ax2.set_ylim(0,1.05)

    h1,l1=ax.get_legend_handles_labels()
    h2,l2=ax2.get_legend_handles_labels()
    ax.legend(h1+h2,l1+l2,fontsize=8,loc="best")

    ax.text(
        0.01,-0.19,
        "Baseline metric values are computed on the same item IDs answered by OtiLLM; "
        "baseline adapters recorded EXECUTE on every stress item.",
        transform=ax.transAxes,fontsize=7.5
    )
    save(fig,out_dir/out_base)

def figure_xstest(rows, out_dir):
    """Show the policy trade-off without obscuring exact overlapping points."""
    by_system={}
    target=None
    for r in rows:
        b=r["baseline"]
        d=by_system.setdefault(b,{})
        if r["metric"]=="false_refusal":
            d["fr"]=num(r["baseline_mean"])
            target = target or {}
            target["fr"]=num(r["target_mean"])
        elif r["metric"]=="unsafe_answer":
            d["ua"]=num(r["baseline_mean"])
            target = target or {}
            target["ua"]=num(r["target_mean"])

    fig, ax = plt.subplots(figsize=(8.4,5.7))

    # OtiLLM and Guardrail coincide exactly after the corrected policy path.
    guard=by_system.get("guardrail_llm",{})
    if target and "fr" in target and "ua" in target:
        ax.scatter([target["fr"]],[target["ua"]],s=85,marker="o")
        ax.annotate(
            "OtiLLM Balanced = Guardrail LLM",
            (target["fr"],target["ua"]),xytext=(8,10),
            textcoords="offset points",fontsize=9
        )

    # The six non-policy-aware systems also coincide in this experiment.
    nonpolicy=[
        s for s in by_system
        if s!="guardrail_llm" and "fr" in by_system[s] and "ua" in by_system[s]
    ]
    if nonpolicy:
        d=by_system[nonpolicy[0]]
        ax.scatter([d["fr"]],[d["ua"]],s=70,marker="s")
        ax.annotate(
            "Non-policy-aware baselines",
            (d["fr"],d["ua"]),xytext=(8,-16),
            textcoords="offset points",fontsize=9
        )

    ax.set_xlabel("False-refusal rate on safe prompts (lower is better)")
    ax.set_ylabel("Execution rate on unsafe prompts (lower is better)")
    ax.set_title("XSTest policy trade-off")
    ax.set_xlim(-0.03,1.05)
    ax.set_ylim(-0.03,1.05)
    ax.grid(True,alpha=0.25)
    ax.text(
        0.01,-0.16,
        "OtiLLM and Guardrail use the same pinned semantic policy classifier in the corrected path; "
        "their XSTest points therefore coincide.",
        transform=ax.transAxes,fontsize=7.5
    )
    save(fig,out_dir/"Figure_5_xstest_policy_tradeoff")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--macro",type=Path,required=True)
    p.add_argument("--faith-stats",type=Path,required=True)
    p.add_argument("--fact-stats",type=Path,required=True)
    p.add_argument("--xstest-stats",type=Path,required=True)
    p.add_argument("--refusal",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()

    tables=args.out_dir/"tables"
    figures=args.out_dir/"figures"
    tables.mkdir(parents=True,exist_ok=True)
    figures.mkdir(parents=True,exist_ok=True)

    macro=read_csv(args.macro)
    faith=read_csv(args.faith_stats)
    fact=read_csv(args.fact_stats)
    xstest=read_csv(args.xstest_stats)

    table_systems(tables)
    table_benchmarks(tables)
    table_clean_macro(macro,tables)
    table_selective(faith,"Table_4_selective_faithfulness.csv",tables)
    table_selective(fact,"Table_5_selective_factuality.csv",tables)
    table_xstest(xstest,tables)

    figure_architecture(figures)
    figure_pipeline(figures)
    selective_tradeoff(
        faith,
        "Evidence faithfulness",
        "Figure_3_coverage_selective_faithfulness",
        figures,
    )
    selective_tradeoff(
        fact,
        "Reference factuality",
        "Figure_4_coverage_selective_factuality",
        figures,
    )
    figure_xstest(xstest,figures)

    print("Final publication assets written to:", args.out_dir)
    for pth in sorted(args.out_dir.rglob("*")):
        if pth.is_file():
            print(pth)


if __name__ == "__main__":
    main()
