"""Create a tiny deterministic publication smoke subset from the frozen manifest.

This utility is not part of the reported benchmark. It exists only to verify the
end-to-end Colab/GPU pipeline before spending compute on the full 1,250-item run.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


DEFAULT_COUNTS = {
    "truthfulqa": 3,
    "fever": 3,
    "hotpotqa": 3,
    "natural_questions": 3,
    "xstest": 4,
}


def rank_key(seed: int, record_id: str) -> str:
    return hashlib.sha256(f"{seed}|smoke|{record_id}".encode("utf-8")).hexdigest()


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
    for dataset, n in DEFAULT_COUNTS.items():
        rows = sorted(grouped[dataset], key=lambda r: rank_key(args.seed, r["id"]))
        if dataset == "xstest":
            # Guarantee the smoke test exercises both execute and refuse paths.
            safe = [r for r in rows if r["policy_label"] == "answer"][:2]
            unsafe = [r for r in rows if r["policy_label"] == "refuse"][:2]
            chosen = safe + unsafe
        else:
            chosen = rows[:n]
        if len(chosen) != n:
            raise RuntimeError(f"{dataset}: requested {n}, found {len(chosen)}")
        selected.extend(chosen)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"smoke_records={len(selected)}")
    print("composition=" + json.dumps(DEFAULT_COUNTS, sort_keys=True))
    print("note=Smoke subset is pipeline validation only and must never enter manuscript results.")


if __name__ == "__main__":
    main()
