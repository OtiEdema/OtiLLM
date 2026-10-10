"""Create a tiny deterministic GPU diagnostic subset from the frozen manifest.

This six-item subset exercises the major publication pathways while minimizing
Colab compute use. It is pipeline validation only and must never enter the
reported manuscript results.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def rank_key(seed: int, record_id: str) -> str:
    return hashlib.sha256(f"{seed}|micro-smoke|{record_id}".encode("utf-8")).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    grouped = defaultdict(list)
    with args.manifest.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                grouped[r["dataset"]].append(r)

    selected = []
    for dataset in ("truthfulqa", "fever", "hotpotqa", "natural_questions"):
        rows = sorted(grouped[dataset], key=lambda r: rank_key(args.seed, r["id"]))
        if not rows:
            raise RuntimeError(f"No rows found for {dataset}")
        selected.append(rows[0])

    xrows = sorted(grouped["xstest"], key=lambda r: rank_key(args.seed, r["id"]))
    safe = next((r for r in xrows if r["policy_label"] == "answer"), None)
    unsafe = next((r for r in xrows if r["policy_label"] == "refuse"), None)
    if safe is None or unsafe is None:
        raise RuntimeError("XSTest micro-smoke requires one safe and one unsafe item.")
    selected.extend([safe, unsafe])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("micro_smoke_records=6")
    print("composition={truthfulqa:1, fever:1, hotpotqa:1, natural_questions:1, xstest:2}")
    print("note=Diagnostic subset only; exclude from manuscript results.")


if __name__ == "__main__":
    main()
