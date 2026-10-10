"""Run clean JAIR experiments and persist one raw row per example/system.

The runner supports checkpointed resume so an interrupted GPU run does not
silently restart or duplicate completed observations.
"""

import argparse
import hashlib
import json
from pathlib import Path

from adapters import ExternalAdapter, OtiLLMAdapter
from backends import load_backend
from baseline_adapters import (
    DirectLLMAdapter, PromptChainAdapter, StandardRAGAdapter, StrongRAGAdapter,
    SelfCheckingAdapter, GuardrailAdapter, ReActAdapter,
)
from metrics import exact_match, faithfulness_placeholder, refusal_metrics, token_f1


BASELINES = {
    "direct_llm": DirectLLMAdapter,
    "prompt_chain": PromptChainAdapter,
    "standard_rag": StandardRAGAdapter,
    "strong_rag": StrongRAGAdapter,
    "self_checking_llm": SelfCheckingAdapter,
    "guardrail_llm": GuardrailAdapter,
    "react_agent": ReActAdapter,
}


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_systems(path, backend):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    adapters = []
    for cfg in data["systems"]:
        if not cfg.get("enabled", False):
            continue
        if cfg["adapter"] == "otillm":
            adapters.append(
                OtiLLMAdapter(cfg["name"], cfg.get("mode", "balanced"), backend)
            )
        else:
            cls = BASELINES[cfg["name"]]
            adapters.append(
                ExternalAdapter(cfg["name"], cls(cfg["name"], backend))
            )
    return adapters


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


def shard_for(record_id: str, num_shards: int) -> int:
    digest = hashlib.sha256(str(record_id).encode("utf-8")).hexdigest()
    return int(digest, 16) % num_shards


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--systems", required=True)
    p.add_argument("--backend", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--num-shards", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    args = p.parse_args()

    if args.num_shards < 1:
        p.error("--num-shards must be >= 1")
    if not 0 <= args.shard_index < args.num_shards:
        p.error("--shard-index must satisfy 0 <= index < num_shards")

    backend = load_backend(args.backend)
    systems = load_systems(args.systems, backend)
    records = [
        r for r in load_jsonl(args.manifest)
        if shard_for(r["id"], args.num_shards) == args.shard_index
    ]
    print(
        f"shard={args.shard_index}/{args.num_shards} "
        f"records_in_shard={len(records)}"
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = completed_keys(out_path) if args.resume else set()
    mode = "a" if args.resume and out_path.exists() else "w"

    written = 0
    skipped = 0
    with out_path.open(mode, encoding="utf-8") as f:
        for record in records:
            for adapter in systems:
                key = (record["id"], adapter.name, "clean")
                if key in done:
                    skipped += 1
                    continue

                out = adapter.run(record, record.get("evidence_clean", []))
                policy_task = (
                    record.get("metadata", {}).get("task_type") == "policy_refusal"
                )
                metrics = {
                    "exact_match": None if policy_task else exact_match(
                        out["answer"], record.get("references", [])
                    ),
                    "token_f1": None if policy_task else token_f1(
                        out["answer"], record.get("references", [])
                    ),
                    "faithfulness": faithfulness_placeholder(),
                }
                metrics.update(
                    refusal_metrics(
                        out["action"], record.get("policy_label", "answer")
                    )
                )
                row = {
                    "id": record["id"],
                    "dataset": record["dataset"],
                    "condition": "clean",
                    "backend": backend.name,
                    "task_type": record.get("metadata", {}).get(
                        "task_type", "content"
                    ),
                    **out,
                    **metrics,
                }
                f.write(json.dumps(row, default=str) + "\n")
                f.flush()
                written += 1

    print(
        f"completed_new={written} skipped_existing={skipped} "
        f"output={out_path}"
    )


if __name__ == "__main__":
    main()
