"""Validate a frozen JAIR benchmark manifest before any experiment is run."""

import argparse
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    "id","dataset","query","references","evidence_clean",
    "gold_evidence_ids","policy_label","metadata"
}
POLICY = {"answer","refuse","defer"}
CONTENT = {"truthfulqa","fever","hotpotqa","natural_questions"}


def validate(path: Path, expected_content_n=None, require_full_xstest=False):
    ids = set()
    datasets = Counter()
    errors = []
    warnings = []
    xstest_labels = Counter()
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
            elif not all(isinstance(x, str) for x in r["references"]):
                errors.append(
                    f"line {lineno}: all references must be strings; "
                    f"got {[type(x).__name__ for x in r['references']]}"
                )
            if r["policy_label"] not in POLICY:
                errors.append(
                    f"line {lineno}: invalid policy_label {r['policy_label']!r}"
                )

            evidence_ids = [x.get("id") for x in r["evidence_clean"]]
            if len(evidence_ids) != len(set(evidence_ids)):
                errors.append(f"line {lineno}: duplicate evidence ids")
            unknown_gold = set(r["gold_evidence_ids"]) - set(evidence_ids)
            if unknown_gold:
                errors.append(
                    f"line {lineno}: gold evidence ids absent from evidence_clean: "
                    f"{sorted(unknown_gold)}"
                )

            ds = r["dataset"]
            if ds == "hotpotqa" and not r["gold_evidence_ids"]:
                errors.append(f"line {lineno}: HotpotQA item lacks gold supporting facts")
            if ds == "natural_questions" and not r["evidence_clean"]:
                errors.append(f"line {lineno}: Natural Questions item lacks bounded evidence")
            if ds == "fever":
                label = r.get("metadata", {}).get("fever_label")
                if label not in {"SUPPORTS", "REFUTES"}:
                    errors.append(
                        f"line {lineno}: FEVER label must be SUPPORTS/REFUTES; got {label!r}"
                    )
                if r["references"] != [label]:
                    errors.append(
                        f"line {lineno}: FEVER reference does not match label {label!r}"
                    )
                if not r["gold_evidence_ids"]:
                    errors.append(
                        f"line {lineno}: FEVER {label} item lacks resolved evidence"
                    )
            if ds == "truthfulqa" and r["evidence_clean"]:
                warnings.append(
                    f"line {lineno}: TruthfulQA unexpectedly contains benchmark evidence"
                )
            if ds == "xstest":
                label = str(r.get("metadata", {}).get("xstest_label", "")).lower()
                xstest_labels[label] += 1
                expected_policy = "answer" if label == "safe" else "refuse"
                if label not in {"safe","unsafe"}:
                    errors.append(f"line {lineno}: invalid XSTest label {label!r}")
                elif r["policy_label"] != expected_policy:
                    errors.append(
                        f"line {lineno}: XSTest policy label inconsistent with {label}"
                    )

    if expected_content_n is not None:
        for ds in sorted(CONTENT):
            if datasets[ds] != expected_content_n:
                errors.append(
                    f"dataset count mismatch: {ds}={datasets[ds]}, "
                    f"expected={expected_content_n}"
                )

    if require_full_xstest:
        if datasets["xstest"] != 450:
            errors.append(
                f"XSTest count mismatch: {datasets['xstest']}, expected 450"
            )
        if xstest_labels["safe"] != 250 or xstest_labels["unsafe"] != 200:
            errors.append(
                "XSTest class mismatch: "
                f"safe={xstest_labels['safe']} unsafe={xstest_labels['unsafe']}; "
                "expected safe=250 unsafe=200"
            )

    return n, datasets, xstest_labels, errors, warnings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--expected-content-n", type=int, default=None)
    p.add_argument("--require-full-xstest", action="store_true")
    args = p.parse_args()

    n, datasets, xlabels, errors, warnings = validate(
        args.manifest,
        expected_content_n=args.expected_content_n,
        require_full_xstest=args.require_full_xstest,
    )
    print(f"records={n}")
    print("datasets=" + json.dumps(dict(sorted(datasets.items()))))
    if xlabels:
        print("xstest_labels=" + json.dumps(dict(sorted(xlabels.items()))))
    for w in warnings:
        print("WARNING:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        raise SystemExit(1)
    print("manifest_valid=true")


if __name__ == "__main__":
    main()
