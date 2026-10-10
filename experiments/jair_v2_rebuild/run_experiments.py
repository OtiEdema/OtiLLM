"""Run clean JAIR experiments and save one raw row per example/system."""

import argparse
import json
from pathlib import Path

from adapters import ExternalAdapter, OtiLLMAdapter
from metrics import exact_match, faithfulness_placeholder, refusal_metrics, token_f1


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_systems(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    adapters = []
    for cfg in data["systems"]:
        if not cfg.get("enabled", False):
            continue
        if cfg["adapter"] == "otillm":
            adapters.append(OtiLLMAdapter(cfg["name"], cfg.get("mode", "balanced")))
        else:
            adapters.append(ExternalAdapter(cfg["name"]))
    return adapters


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--systems", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    rows = []
    for record in load_jsonl(args.manifest):
        for adapter in load_systems(args.systems):
            out = adapter.run(record, record.get("evidence_clean", []))
            metrics = {
                "exact_match": exact_match(out["answer"], record.get("references", [])),
                "token_f1": token_f1(out["answer"], record.get("references", [])),
                "faithfulness": faithfulness_placeholder(),
            }
            metrics.update(refusal_metrics(out["action"], record.get("policy_label", "answer")))
            rows.append({
                "id": record["id"],
                "dataset": record["dataset"],
                "condition": "clean",
                "references": record.get("references", []),
                **out,
                **metrics,
            })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, default=str) + "\n")
    print(f"Saved {len(rows)} raw observations to {out_path}")


if __name__ == "__main__":
    main()
