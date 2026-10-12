"""Attach independent factuality and evidence-faithfulness scores to raw outputs."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

from claim_evaluation import NLIEvaluator


def load_manifest(path: Path):
    out = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def completed_keys(path: Path):
    done = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            done.add((r["id"], r["system"], r.get("condition", "clean")))
    return done


def shard_for(row, num_shards: int) -> int:
    key = f'{row["id"]}|{row["system"]}|{row.get("condition", "clean")}'
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest, 16) % num_shards


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--nli-model", required=True)
    p.add_argument("--nli-revision", default=None)
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--num-shards", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    args = p.parse_args()

    if args.num_shards < 1:
        p.error("--num-shards must be >= 1")
    if not 0 <= args.shard_index < args.num_shards:
        p.error("--shard-index must satisfy 0 <= index < num_shards")

    manifest = load_manifest(args.manifest)
    evaluator = NLIEvaluator(args.nli_model, revision=args.nli_revision)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = completed_keys(args.out) if args.resume else set()
    mode = "a" if args.resume and args.out.exists() else "w"

    n = 0
    skipped = 0
    eligible = 0
    run_start = perf_counter()
    with args.raw.open("r", encoding="utf-8") as fin, args.out.open(mode, encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            if shard_for(row, args.num_shards) != args.shard_index:
                continue
            eligible += 1
            key = (row["id"], row["system"], row.get("condition", "clean"))
            if key in done:
                skipped += 1
                continue
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
            fout.flush()
    elapsed = perf_counter() - run_start
    rate = (n / elapsed * 60.0) if elapsed > 0 else 0.0
    print(
        f"shard={args.shard_index}/{args.num_shards} eligible={eligible} "
        f"completed_new={n} skipped_existing={skipped} "
        f"elapsed_seconds={elapsed:.2f} observations_per_minute={rate:.3f} "
        f"output={args.out}"
    )


if __name__ == "__main__":
    main()
