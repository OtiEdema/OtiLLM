"""Freeze manifest provenance and checksums for publication."""

import argparse
import hashlib
import json
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_value(args):
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--metadata-out", type=Path, required=True)
    args = p.parse_args()

    counts = Counter()
    ids = []
    with args.manifest.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                counts[r["dataset"]] += 1
                ids.append(r["id"])

    metadata = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(args.manifest),
        "manifest_sha256": sha256(args.manifest),
        "selection_seed": args.seed,
        "record_count": len(ids),
        "dataset_counts": dict(sorted(counts.items())),
        "id_list_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]),
        "python_version": platform.python_version(),
    }
    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
