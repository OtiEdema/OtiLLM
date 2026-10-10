"""Validate a JAIR benchmark manifest before any experiment is run."""

import argparse
import json
from collections import Counter
from pathlib import Path

REQUIRED = {"id","dataset","query","references","evidence_clean","gold_evidence_ids","policy_label","metadata"}
POLICY = {"answer","refuse","defer"}


def validate(path: Path):
    ids = set()
    datasets = Counter()
    errors = []
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            n += 1
            try:
                r = json.loads(line)
            except Exception as e:
                errors.append(f"line {lineno}: invalid JSON: {e}")
                continue
            missing = REQUIRED - set(r)
            if missing:
                errors.append(f"line {lineno}: missing {sorted(missing)}")
                continue
            if r["id"] in ids:
                errors.append(f"line {lineno}: duplicate id {r['id']}")
            ids.add(r["id"])
            datasets[r["dataset"]] += 1
            if not isinstance(r["query"], str) or not r["query"].strip():
                errors.append(f"line {lineno}: empty query")
            if not isinstance(r["references"], list) or not r["references"]:
                errors.append(f"line {lineno}: references must be a non-empty list")
            if r["policy_label"] not in POLICY:
                errors.append(f"line {lineno}: invalid policy_label {r['policy_label']!r}")
            evidence_ids = [x.get("id") for x in r["evidence_clean"]]
            if len(evidence_ids) != len(set(evidence_ids)):
                errors.append(f"line {lineno}: duplicate evidence ids")
            unknown_gold = set(r["gold_evidence_ids"]) - set(evidence_ids)
            if unknown_gold:
                errors.append(f"line {lineno}: gold evidence ids absent from evidence_clean: {sorted(unknown_gold)}")
    return n, datasets, errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    args = p.parse_args()
    n, datasets, errors = validate(args.manifest)
    print(f"records={n}")
    print("datasets=" + json.dumps(dict(sorted(datasets.items()))))
    if errors:
        for e in errors:
            print("ERROR:", e)
        raise SystemExit(1)
    print("manifest_valid=true")


if __name__ == "__main__":
    main()
