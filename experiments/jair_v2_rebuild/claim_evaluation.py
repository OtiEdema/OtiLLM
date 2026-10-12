"""Independent claim-level evaluation utilities.

The evaluator keeps factuality and evidence faithfulness separate. It supports
a configurable NLI model through transformers and also exports human-review rows
for adjudication. No score is manufactured if the evaluator is unavailable.
"""

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, List


def split_claims(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", (text or "").strip())
    return [c.strip(" -\t") for c in chunks if len(c.strip()) >= 3]


class NLIEvaluator:
    def __init__(self, model_name: str, revision: str | None = None):
        try:
            import torch
            from transformers import pipeline
        except ImportError as e:
            raise RuntimeError("Install transformers and torch to use NLI evaluation.") from e
        self.model_name = model_name
        self.revision = revision
        device = 0 if torch.cuda.is_available() else -1
        self.device = "cuda:0" if device == 0 else "cpu"
        self.pipe = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            revision=revision,
            return_all_scores=True,
            device=device,
        )
        print(f"NLI evaluator device={self.device}")

    def entailment_probability(self, premise: str, hypothesis: str) -> float:
        outputs = self.pipe({"text": premise, "text_pair": hypothesis})[0]
        probs = {str(x["label"]).lower(): float(x["score"]) for x in outputs}
        for key, value in probs.items():
            if "entail" in key:
                return value
        raise RuntimeError(f"Could not identify entailment label from {sorted(probs)}")

    def score_faithfulness(self, answer: str, evidence: List[Dict], threshold: float = 0.5) -> Dict:
        claims = split_claims(answer)
        premise = "\n".join(str(x.get("content", "")) for x in evidence)
        if not claims:
            return {"claim_count": 0, "supported_claim_count": 0, "faithfulness": 1.0, "unsupported_claim_rate": 0.0, "claim_scores": []}
        scores = [self.entailment_probability(premise, claim) if premise else 0.0 for claim in claims]
        supported = sum(s >= threshold for s in scores)
        return {
            "claim_count": len(claims),
            "supported_claim_count": supported,
            "faithfulness": supported / len(claims),
            "unsupported_claim_rate": 1.0 - supported / len(claims),
            "claim_scores": [{"claim": c, "entailment": s} for c, s in zip(claims, scores)],
        }

    def score_reference_factuality(self, answer: str, references: List[str]) -> float:
        if not references:
            return float("nan")
        # Bidirectional check reduces the chance that a short answer merely mentions
        # a reference while adding a contradiction.
        forward = max(self.entailment_probability(r, answer) for r in references)
        backward = max(self.entailment_probability(answer, r) for r in references)
        return min(forward, backward)


def export_human_review(raw_path: Path, manifest_path: Path, out_csv: Path):
    manifest = {}
    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                x = json.loads(line); manifest[x["id"]] = x
    rows = []
    with raw_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            r = json.loads(line)
            m = manifest.get(r["id"], {})
            rows.append({
                "id": r["id"],
                "dataset": r.get("dataset"),
                "system": r.get("system"),
                "condition": r.get("condition"),
                "query": m.get("query"),
                "answer": r.get("answer"),
                "references": " || ".join(m.get("references", [])),
                "evidence": " || ".join(x.get("content", "") for x in m.get("evidence_clean", [])),
                "human_correct": "",
                "human_factual": "",
                "human_faithful": "",
                "human_should_refuse": "",
                "reviewer_notes": "",
            })
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("export-human")
    h.add_argument("--raw", type=Path, required=True)
    h.add_argument("--manifest", type=Path, required=True)
    h.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.cmd == "export-human":
        export_human_review(args.raw, args.manifest, args.out)
        print(f"Saved human-adjudication sheet to {args.out}")


if __name__ == "__main__":
    main()
