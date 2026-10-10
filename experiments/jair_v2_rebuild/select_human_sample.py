"""Select a deterministic stratified sample for blinded human adjudication."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def key(seed: int, *parts) -> str:
    joined = "|".join(map(str, parts))
    return hashlib.sha256(f"{seed}|{joined}".encode()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--per-stratum", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    manifest = {}
    with args.manifest.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                manifest[r["id"]] = r

    strata = defaultdict(list)
    with args.raw.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            s = (r.get("dataset"), r.get("system"), r.get("condition", "clean"))
            strata[s].append(r)

    selected = []
    for s, rows in sorted(strata.items()):
        rows = sorted(rows, key=lambda r: key(args.seed, *s, r["id"]))
        selected.extend(rows[:args.per_stratum])

    # Blind system identity behind a stable review_id; keep mapping in a separate file.
    review_rows, mapping_rows = [], []
    for idx, r in enumerate(sorted(selected, key=lambda x: key(args.seed, x["id"], x.get("system"), x.get("condition"))), start=1):
        m = manifest[r["id"]]
        review_id = f"R{idx:05d}"
        evidence = r.get("evaluation_evidence", m.get("evidence_clean", []))
        review_rows.append({
            "review_id": review_id,
            "dataset": r.get("dataset"),
            "condition": r.get("condition"),
            "query": m.get("query"),
            "answer": r.get("answer"),
            "references": " || ".join(m.get("references", [])),
            "evidence": " || ".join(x.get("content", "") for x in evidence),
            "correctness_yes_no_unclear": "",
            "factuality_yes_no_unclear": "",
            "faithfulness_yes_no_unclear": "",
            "refusal_appropriate_yes_no_unclear": "",
            "notes": "",
        })
        mapping_rows.append({
            "review_id": review_id,
            "id": r["id"],
            "system": r.get("system"),
            "dataset": r.get("dataset"),
            "condition": r.get("condition"),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(review_rows[0].keys()))
        w.writeheader(); w.writerows(review_rows)

    mapping = args.out.with_name(args.out.stem + "_blinding_map.csv")
    with mapping.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(mapping_rows[0].keys()))
        w.writeheader(); w.writerows(mapping_rows)

    print(f"review_rows={len(review_rows)}")
    print(f"review_sheet={args.out}")
    print(f"blinding_map={mapping}")


if __name__ == "__main__":
    main()
