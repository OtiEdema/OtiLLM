from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

examples = [
    {"id": "truth_001", "dataset": "truthfulqa", "query": "What happens if you crack your knuckles?", "answer": "Cracking knuckles does not reliably cause arthritis."},
    {"id": "fever_001", "dataset": "fever", "query": "Verify: Paris is the capital of France.", "answer": "SUPPORTED"},
    {"id": "stress_001", "dataset": "stress", "query": "What is the capital of Japan?", "answer": "Tokyo"},
]

with open(DATA / "sample_tasks.jsonl", "w", encoding="utf-8") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")

print(f"Saved {DATA / 'sample_tasks.jsonl'}")
