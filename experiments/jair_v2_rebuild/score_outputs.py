"""Attach independent factuality and evidence-faithfulness scores to raw outputs."""

import argparse
import json
from pathlib import Path

from claim_evaluation import NLIEvaluator


def load_manifest(path: Path):
    out = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--nli-model", required=True)
    p.add_argument("--nli-revision", default=None)
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    manifest = load_manifest(args.manifest)
    evaluator = NLIEvaluator(args.nli_model, revision=args.nli_revision)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with args.raw.open("r", encoding="utf-8") as fin, args.out.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            record = manifest[row["id"]]
            evidence = record.get("evidence_clean", [])
            # Stress outputs are scored against the evidence actually exposed to the
            # system only if that evidence is archived in the raw row. If absent,
            # reconstructing it from clean evidence would be invalid.
            if row.get("condition", "clean") != "clean" and "evaluation_evidence" not in row:
                raise RuntimeError(
                    "Stress row lacks evaluation_evidence. Re-run stress generation with "
                    "the exact transformed evidence archived in each raw row."
                )
            evidence_for_eval = row.get("evaluation_evidence", evidence)
            policy_task = record.get("metadata", {}).get("task_type") == "policy_refusal"
            if policy_task:
                faith = {
                    "claim_count": None,
                    "supported_claim_count": None,
                    "faithfulness": None,
                    "unsupported_claim_rate": None,
                    "claim_scores": [],
                }
                factuality = None
            else:
                faith = evaluator.score_faithfulness(
                    row.get("answer", ""), evidence_for_eval, threshold=args.threshold
                )
                factuality = evaluator.score_reference_factuality(
                    row.get("answer", ""), record.get("references", [])
                )
            row.update(faith)
            row["factuality"] = factuality
            evaluator_id = args.nli_model + ("@" + args.nli_revision if args.nli_revision else "")
            row["factuality_evaluator"] = evaluator_id
            row["faithfulness_evaluator"] = evaluator_id
            row["entailment_threshold"] = args.threshold
            fout.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            n += 1
    print(f"Saved {n} independently scored observations to {args.out}")


if __name__ == "__main__":
    main()
