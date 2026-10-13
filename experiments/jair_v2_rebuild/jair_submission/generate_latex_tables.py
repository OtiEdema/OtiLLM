"""Convert corrected publication CSV assets to JAIR-ready LaTeX tables."""

import argparse
import csv
from pathlib import Path

LABELS = {
    "Direct LLM":"Direct LLM",
    "Prompt Chain":"Prompt Chain",
    "Standard RAG":"Standard RAG",
    "Strong RAG":"Strong RAG",
    "Self-Checking LLM":"Self-Checking LLM",
    "Guardrail LLM":"Guardrail LLM",
    "ReAct":"ReAct",
    "OtiLLM Balanced":"OtiLLM Balanced",
}

def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def fnum(x, d=3):
    try:
        return f"{float(x):.{d}f}"
    except Exception:
        return str(x)

def fp(x):
    try:
        v=float(x)
        if v < 0.001:
            return f"{v:.2e}"
        return f"{v:.4f}"
    except Exception:
        return str(x)

def esc(s):
    return str(s).replace("&", r"\&").replace("_", r"\_").replace("%", r"\%")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def table1(src, out):
    rr=rows(src)
    body="\n".join(
        f"{esc(r['system'])} & {esc(r['model_calls'])} & {esc(r['retrieval'])} & "
        f"{esc(r['policy_gate'])} & {esc(r['selective_execution'])} & "
        f"{esc(r['clean'])} & {esc(r['stress'])} \\\\" for r in rr
    )
    write(out, rf"""\begin{{table*}}[t]
\centering
\caption{{Systems and control mechanisms used in the evaluation. Stress testing is restricted to the retrieval-consuming systems.}}
\label{{tab:systems}}
\small
\begin{{tabular}}{{lcccccc}}
\toprule
System & Calls & Retrieval & Policy gate & Selective execution & Clean & Stress \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table*}}
""")

def table2(src, out):
    rr=rows(src)
    body="\n".join(
        f"{esc(r['benchmark'])} & {r['items']} & {esc(r['role'])} & "
        f"{esc(r['benchmark_native_evidence'])} & {r['clean']} & {r['stress']} & {r['macro_content']} \\\\"
        for r in rr
    )
    write(out, rf"""\begin{{table*}}[t]
\centering
\caption{{Frozen benchmark composition. XSTest is evaluated separately and excluded from content macro averages.}}
\label{{tab:benchmarks}}
\small
\begin{{tabular}}{{lrlcccc}}
\toprule
Benchmark & Items & Role & Native evidence & Clean & Stress & Content macro \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table*}}
""")

def table3(src, out):
    rr=rows(src)
    body="\n".join(
        f"{esc(r['system'])} & {fnum(r['token_f1'])} & {fnum(r['reference_factuality_nli'])} & "
        f"{fnum(r['evidence_faithfulness_nli'])} & {fnum(r['unsupported_claim_rate'])} & "
        f"{fnum(r['coverage'])} & {fnum(r['latency_seconds'])} & {fnum(r['llm_calls'],2)} \\\\"
        for r in rr
    )
    write(out, rf"""\begin{{table*}}[t]
\centering
\caption{{Clean content macro results over TruthfulQA, FEVER, HotpotQA, and Natural Questions. Factuality and faithfulness are automated NLI-based estimates; coverage is reported separately.}}
\label{{tab:clean}}
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
System & Token F1 & Factuality & Faithfulness & Unsupported & Coverage & Latency (s) & LLM calls \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table*}}
""")

def selective(src, out, metric, label):
    rr=rows(src)
    body=[]
    for r in rr:
        sig="*" if r.get("significant_0.05")=="Yes" else ""
        body.append(
            f"{esc(r['condition'].title())} & {esc(r['baseline'])} & {r['n_paired']} & "
            f"{fnum(r['otillm_coverage'])} & {fnum(r['otillm_mean'])} & "
            f"{fnum(r['baseline_mean_on_same_items'])} & {fnum(r['paired_difference'])}{sig} & "
            f"[{fnum(r['ci_2.5'])}, {fnum(r['ci_97.5'])}] & {fp(r['holm_adjusted_p'])} \\\\"
        )
    write(out, rf"""\begin{{table*}}[t]
\centering
\caption{{Paired selective {metric} comparisons on the exact items answered by OtiLLM. Asterisk denotes Holm-adjusted $p<0.05$. Coverage is OtiLLM answer coverage for the condition.}}
\label{{tab:{label}}}
\scriptsize
\begin{{tabular}}{{llrrrrrrr}}
\toprule
Condition & Baseline & $n$ & Coverage & OtiLLM & Baseline & $\Delta$ & 95\% CI & Holm $p$ \\
\midrule
{"".join(body)}
\bottomrule
\end{{tabular}}
\end{{table*}}
""")

def table6(src, out):
    rr=rows(src)
    # Reconstruct one policy outcome row per system from the paired-comparison file.
    systems={}
    target={}
    for r in rr:
        metric=r["metric"]
        baseline=r["baseline"]
        systems.setdefault(baseline,{})[metric]=r["baseline_mean"]
        target[metric]=r["otillm_mean"]
    systems["OtiLLM Balanced"]=target
    order=["Direct LLM","Prompt Chain","Standard RAG","Strong RAG","Self-Checking LLM","ReAct","Guardrail LLM","OtiLLM Balanced"]
    body=[]
    for s in order:
        d=systems.get(s,{})
        if not d: continue
        body.append(
            f"{esc(s)} & {fnum(d.get('refusal_correct',''))} & "
            f"{fnum(d.get('false_refusal',''))} & {fnum(d.get('unsafe_answer',''))} \\\\"
        )
    write(out, rf"""\begin{{table}}[t]
\centering
\caption{{Corrected XSTest policy outcomes. OtiLLM and Guardrail LLM coincide because the corrected path uses the same pinned semantic policy classifier and instruction.}}
\label{{tab:xstest}}
\small
\begin{{tabular}}{{lrrr}}
\toprule
System & Policy correct & False refusal & Unsafe answer \\
\midrule
{"".join(body)}
\bottomrule
\end{{tabular}}
\end{{table}}
""")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a=p.parse_args()
    t=a.asset_dir/"tables"
    table1(t/"Table_1_systems_and_controls.csv", a.out_dir/"table1_systems.tex")
    table2(t/"Table_2_benchmark_composition.csv", a.out_dir/"table2_benchmarks.tex")
    table3(t/"Table_3_clean_content_macro.csv", a.out_dir/"table3_clean.tex")
    selective(t/"Table_4_selective_faithfulness.csv", a.out_dir/"table4_faithfulness.tex", "evidence faithfulness", "selective-faithfulness")
    selective(t/"Table_5_selective_factuality.csv", a.out_dir/"table5_factuality.tex", "reference factuality", "selective-factuality")
    table6(t/"Table_6_xstest_policy.csv", a.out_dir/"table6_xstest.tex")
    for x in sorted(a.out_dir.glob("*.tex")):
        print(x)

if __name__=="__main__":
    main()
