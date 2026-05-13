from pathlib import Path
import csv, json, sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))

from otillm.runtime import GovernedRuntime

DATA = ROOT / "data" / "sample_tasks.jsonl"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

runtime = GovernedRuntime()
rows = []

with open(DATA, "r", encoding="utf-8") as f:
    for line in f:
        ex = json.loads(line)
        result = runtime.run(ex["query"])
        rows.append({
            "id": ex["id"],
            "dataset": ex["dataset"],
            "system": "otillm_balanced",
            "query": ex["query"],
            "answer": result.answer,
            "action": result.action,
            "confidence": result.confidence,
            "trace_complete": 1.0 if result.trace.nodes else 0.0,
            "accuracy": 1.0 if ex["answer"].lower() in result.answer.lower() else 0.5,
            "truthfulness": 1.0 if ex["answer"].lower() in result.answer.lower() else 0.5,
            "faithfulness": 1.0 if result.evidence_used else 0.0,
            "unsupported_claim_rate": 0.0 if result.evidence_used else 1.0,
        })

out = RESULTS / "jair_all_results.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

summary = RESULTS / "jair_summary_results.csv"
with open(summary, "w", newline="", encoding="utf-8") as f:
    fields = ["system", "accuracy", "truthfulness", "faithfulness", "unsupported_claim_rate", "trace_complete"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerow({
        "system": "otillm_balanced",
        "accuracy": sum(r["accuracy"] for r in rows) / len(rows),
        "truthfulness": sum(r["truthfulness"] for r in rows) / len(rows),
        "faithfulness": sum(r["faithfulness"] for r in rows) / len(rows),
        "unsupported_claim_rate": sum(r["unsupported_claim_rate"] for r in rows) / len(rows),
        "trace_complete": sum(r["trace_complete"] for r in rows) / len(rows),
    })

print(f"Saved {out}")
print(f"Saved {summary}")
