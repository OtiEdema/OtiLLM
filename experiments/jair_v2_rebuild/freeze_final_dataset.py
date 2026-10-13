"""Freeze the corrected final merged dataset used for JAIR analysis."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--metadata-out", type=Path, required=True)
    args = p.parse_args()

    rows = []
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    keys = [
        (r.get("id"), r.get("system"), r.get("condition", "clean"))
        for r in rows
    ]
    unique = len(set(keys))
    duplicates = len(rows) - unique

    systems = Counter(r.get("system") for r in rows)
    datasets = Counter(r.get("dataset") for r in rows)
    conditions = Counter(r.get("condition", "clean") for r in rows)

    meta = {
        "file": str(args.input),
        "sha256": sha256(args.input),
        "rows": len(rows),
        "unique_keys": unique,
        "duplicate_keys": duplicates,
        "systems": dict(sorted(systems.items())),
        "datasets": dict(sorted(datasets.items())),
        "conditions": dict(sorted(conditions.items())),
    }

    if len(rows) != 26000:
        raise SystemExit(f"Expected 26000 rows, observed {len(rows)}")
    if duplicates != 0:
        raise SystemExit(f"Expected 0 duplicate keys, observed {duplicates}")

    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
