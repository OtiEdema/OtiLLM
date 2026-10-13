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
        {"system":"Standard RAG","model_calls":"1","retrieval":"Yes","policy_gate":"No","selective_execution":"Prompt-level only","clean":"Yes","stress":"Yes"},
        {"system":"Strong RAG","model_calls":"1","retrieval":"Yes + reranking","policy_gate":"No","selective_execution":"Prompt-level only","clean":"Yes","stress":"Yes"},
        {"system":"Self-Checking LLM","model_calls":"2","retrieval":"No","policy_gate":"No","selective_execution":"No","clean":"Yes","stress":"No"},
        {"system":"Guardrail LLM","model_calls":"1-2","retrieval":"No","policy_gate":"Yes","selective_execution":"Policy refusal","clean":"Yes","stress":"No"},
        {"system":"ReAct","model_calls":"2","retrieval":"Yes","policy_gate":"No","selective_execution":"Prompt-level only","clean":"Yes","stress":"Yes"},
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
            "significant_0.05": "Yes" if (num(r["holm_adjusted_p"]) or 1) < 0.05 else "No",
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
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis("off")
    boxes = [
        (0.03,0.68,0.13,0.16,"Query"),
        (0.20,0.68,0.15,0.16,"Policy\nGate"),
        (0.39,0.68,0.16,0.16,"Evidence\nRetrieval"),
        (0.59,0.68,0.16,0.16,"Evidence\nSufficiency"),
        (0.79,0.68,0.16,0.16,"Confidence\nGate"),
        (0.59,0.30,0.16,0.16,"Generate"),
        (0.79,0.30,0.16,0.16,"Execute"),
        (0.39,0.30,0.16,0.16,"Defer"),
        (0.20,0.30,0.15,0.16,"Policy\nRefuse"),
    ]
    for x,y,w,h,label in boxes:
        ax.add_patch(plt.Rectangle((x,y),w,h,fill=False,linewidth=1.4))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=10)
    arrows = [
        ((0.16,0.76),(0.20,0.76)),((0.35,0.76),(0.39,0.76)),
        ((0.55,0.76),(0.59,0.76)),((0.75,0.76),(0.79,0.76)),
        ((0.87,0.68),(0.67,0.46)),((0.75,0.38),(0.79,0.38)),
        ((0.67,0.68),(0.47,0.46)),((0.275,0.68),(0.275,0.46)),
    ]
    for a,b in arrows:
        ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="->",linewidth=1.2))
    ax.text(0.5,0.95,"Validated OtiLLM publication runtime",ha="center",fontsize=14)
    ax.text(0.5,0.10,
            "Broader architectural extensions (not fully validated here): retrieval reconsideration,\n"
            "formal utility optimisation, longitudinal governed memory, learned action policy",
            ha="center",va="center",fontsize=9)
    save(fig,out_dir/"Figure_1_governed_runtime_architecture")


def figure_pipeline(out_dir):
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    labels = [
        "Frozen\nmanifest",
        "Clean\ngeneration",
        "Stress\ngeneration",
        "Shard merge +\nintegrity checks",
        "Independent\nNLI scoring",
        "Aggregate +\nselective stats",
        "Tables +\nfigures",
    ]
    xs = [0.02,0.16,0.30,0.44,0.60,0.75,0.89]
    widths=[0.10,0.10,0.10,0.12,0.11,0.11,0.09]
    for i,(x,w,label) in enumerate(zip(xs,widths,labels)):
        ax.add_patch(plt.Rectangle((x,0.42),w,0.22,fill=False,linewidth=1.3))
        ax.text(x+w/2,0.53,label,ha="center",va="center",fontsize=9)
        if i < len(labels)-1:
            nx=xs[i+1]
            ax.annotate("",xy=(nx,0.53),xytext=(x+w,0.53),
                        arrowprops=dict(arrowstyle="->",linewidth=1.1))
    ax.text(0.5,0.80,"Deterministic publication evaluation pipeline",ha="center",fontsize=14)
    ax.text(0.5,0.22,
            "Persistent checkpointing → resumable runs → frozen merged artefacts → corrected final dataset (26,000 rows)",
            ha="center",fontsize=9)
    save(fig,out_dir/"Figure_2_reproducibility_pipeline")


def selective_tradeoff(rows, metric_name, out_base, out_dir):
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    systems = ["standard_rag","strong_rag","react_agent"]
    markers = ["s","^","D"]
    target_by_cond = {}
    for r in rows:
        target_by_cond.setdefault(r["condition"], (num(r["target_coverage"]), num(r["target_mean"])))
    xs=[]; ys=[]
    for cond in STRESS:
        if cond in target_by_cond:
            x,y=target_by_cond[cond]
            xs.append(x); ys.append(y)
            ax.annotate(cond, (x,y), xytext=(5,5), textcoords="offset points", fontsize=8)
    ax.scatter(xs,ys,marker="o",s=60,label="OtiLLM Balanced")
    for system,marker in zip(systems,markers):
        sx=[]; sy=[]
        for cond in STRESS:
            match=[r for r in rows if r["baseline"]==system and r["condition"]==cond]
            if match:
                sx.append(num(match[0]["target_coverage"]))
                sy.append(num(match[0]["baseline_mean_on_target_answered_subset"]))
        ax.scatter(sx,sy,marker=marker,s=45,label=SYSTEM_LABELS[system])
    ax.set_xlabel("OtiLLM answer coverage (matched subset fraction)")
    ax.set_ylabel(metric_name)
    ax.set_title(f"Coverage–{metric_name.lower()} trade-off under retrieval stress")
    ax.legend(fontsize=8)
    ax.grid(True,alpha=0.25)
    save(fig,out_dir/out_base)


def figure_xstest(rows, out_dir):
    # Recover one point per system from false-refusal and unsafe-answer families.
    by_system={}
    for r in rows:
        b=r["baseline"]
        d=by_system.setdefault(b,{})
        if r["metric"]=="false_refusal":
            d["false_refusal_baseline"]=num(r["baseline_mean"])
            d["false_refusal_target"]=num(r["target_mean"])
        elif r["metric"]=="unsafe_answer":
            d["unsafe_answer_baseline"]=num(r["baseline_mean"])
            d["unsafe_answer_target"]=num(r["target_mean"])

    fig, ax = plt.subplots(figsize=(8,5.5))
    # OtiLLM from any complete row.
    sample=next(d for d in by_system.values() if "false_refusal_target" in d and "unsafe_answer_target" in d)
    ax.scatter([sample["false_refusal_target"]],[sample["unsafe_answer_target"]],s=70,marker="o",label="OtiLLM Balanced")
    ax.annotate("OtiLLM", (sample["false_refusal_target"],sample["unsafe_answer_target"]),
                xytext=(5,5),textcoords="offset points",fontsize=8)

    markers=["s","^","D","v","P","X","<"]
    for (system,d),marker in zip(sorted(by_system.items()),markers):
        if "false_refusal_baseline" not in d or "unsafe_answer_baseline" not in d:
            continue
        x=d["false_refusal_baseline"]; y=d["unsafe_answer_baseline"]
        ax.scatter([x],[y],s=50,marker=marker,label=SYSTEM_LABELS.get(system,system))
        ax.annotate(SYSTEM_LABELS.get(system,system),(x,y),xytext=(5,5),textcoords="offset points",fontsize=7)
    ax.set_xlabel("False-refusal rate on safe prompts (lower is better)")
    ax.set_ylabel("Unsafe-answer rate on unsafe prompts (lower is better)")
    ax.set_title("XSTest policy trade-off")
    ax.grid(True,alpha=0.25)
    ax.legend(fontsize=7,loc="best")
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
