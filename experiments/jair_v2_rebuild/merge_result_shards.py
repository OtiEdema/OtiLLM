"""Merge deterministic JAIR result shards and validate uniqueness/completeness."""

import argparse
import glob
import json
from collections import Counter
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--glob", dest="pattern", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected-rows", type=int, default=None)
    args = p.parse_args()

    files = sorted(glob.glob(args.pattern))
    if not files:
        raise SystemExit(f"No shard files matched: {args.pattern}")

    rows = []
    keys = set()
    duplicates = []
    systems = Counter()
    datasets = Counter()
    conditions = Counter()

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                r = json.loads(line)
                key = (r["id"], r["system"], r.get("condition", "clean"))
                if key in keys:
                    duplicates.append((fp, lineno, key))
                    continue
                keys.add(key)
                rows.append(r)
                systems[r["system"]] += 1
                datasets[r["dataset"]] += 1
                conditions[r.get("condition", "clean")] += 1

    if duplicates:
        sample = duplicates[:10]
        raise SystemExit(f"Duplicate result keys detected ({len(duplicates)}): {sample}")

    if args.expected_rows is not None and len(rows) != args.expected_rows:
        raise SystemExit(
            f"Row-count mismatch: got {len(rows)}, expected {args.expected_rows}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

    print(f"files={len(files)}")
    print(f"rows={len(rows)}")
    print(f"unique_keys={len(keys)}")
    print("systems=" + json.dumps(dict(sorted(systems.items()))))
    print("datasets=" + json.dumps(dict(sorted(datasets.items()))))
    print("conditions=" + json.dumps(dict(sorted(conditions.items()))))
    print(f"merged_output={args.out}")


if __name__ == "__main__":
    main()
