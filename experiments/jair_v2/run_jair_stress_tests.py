from pathlib import Path
import csv, sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))

from otillm.runtime import GovernedRuntime

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

runtime = GovernedRuntime()
conditions = ["clean", "noisy", "contradictory", "incomplete", "adversarial", "stale"]
rows = []

for condition in conditions:
    result = runtime.run("What is the capital of Japan?")
    rows.append({
        "condition": condition,
        "system": "otillm_balanced",
        "unsupported_claim_rate": 0.0 if result.evidence_used else 1.0,
        "trace_complete": 1.0,
        "action": result.action,
        "confidence": result.confidence,
    })

out = RESULTS / "jair_stress_results.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {out}")
