"""Build a deterministic JAIR manifest from locally acquired benchmark files.

This script does not silently download or transform benchmark data from unofficial
sources. Acquire the benchmark files from the sources recorded in configs/benchmarks.json
and pass them explicitly. This preserves provenance and makes licences auditable.
"""

import argparse
import csv
import html
import json
import random
import re
from pathlib import Path
from typing import Dict, Iterable, List


def stable_sample(rows: List[Dict], n: int, seed: int) -> List[Dict]:
    rows = list(rows)
    rng = random.Random(seed)
    if n >= len(rows):
        return rows
    idx = sorted(rng.sample(range(len(rows)), n))
    return [rows[i] for i in idx]


def write_jsonl(rows: Iterable[Dict], out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def truthfulqa(path: Path, n: int, seed: int) -> List[Dict]:
    """Parse the official TruthfulQA CSV used by the original repository."""
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            q = r.get("Question") or r.get("question")
            best = r.get("Best Answer") or r.get("best_answer")
            correct = r.get("Correct Answers") or r.get("correct_answers") or ""
            if not q or not best:
                continue
            refs = [best]
            for x in str(correct).split(";"):
                x = x.strip()
                if x and x not in refs:
                    refs.append(x)
            rows.append({
                "id": f"truthfulqa_{i:04d}",
                "dataset": "truthfulqa",
                "query": q,
                "references": refs,
                "evidence_clean": [],
                "gold_evidence_ids": [],
                "policy_label": "answer",
                "metadata": {
                    "category": r.get("Category") or r.get("category"),
                    "type": r.get("Type") or r.get("type"),
                    "source": r.get("Source") or r.get("source"),
                    "benchmark_native_evidence": False,
                },
            })
    return stable_sample(rows, n, seed)


def hotpotqa(path: Path, n: int, seed: int) -> List[Dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for ex in data:
        sf = {(t, int(s)) for t, s in ex.get("supporting_facts", [])}
        evidence = []
        gold_ids = []
        for title, sentences in ex.get("context", []):
            for j, sent in enumerate(sentences):
                eid = f"{ex.get('_id', ex.get('id', 'unknown'))}:{title}:{j}"
                item = {
                    "id": eid, "content": sent, "source": title, "trust_score": 1.0,
                    "metadata": {"sentence_id": j, "title": title}
                }
                evidence.append(item)
                if (title, j) in sf:
                    gold_ids.append(eid)
        exid = ex.get("_id") or ex.get("id")
        rows.append({
            "id": f"hotpotqa_{exid}",
            "dataset": "hotpotqa",
            "query": ex["question"],
            "references": [str(ex["answer"])],
            "evidence_clean": evidence,
            "gold_evidence_ids": gold_ids,
            "policy_label": "answer",
            "metadata": {"type": ex.get("type"), "level": ex.get("level")},
        })
    return stable_sample(rows, n, seed)


def fever(claims_path: Path, evidence_lookup_path: Path, n: int, seed: int) -> List[Dict]:
    """Parse FEVER claims plus an explicit evidence lookup JSONL.

    The lookup must contain {"page": str, "line": int, "text": str}.
    This avoids pretending FEVER claim metadata alone contains the evidence text.
    """
    lookup = {}
    with evidence_lookup_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            x = json.loads(line)
            lookup[(str(x["page"]), int(x["line"]))] = str(x["text"])

    rows = []
    with claims_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            ex = json.loads(line)
            label = ex.get("label")
            if label not in {"SUPPORTS", "REFUTES", "NOT ENOUGH INFO"}:
                continue
            evidence = []
            gold_ids = []
            seen = set()
            for group in ex.get("evidence", []) or []:
                for ann in group or []:
                    if len(ann) < 4 or ann[2] is None or ann[3] is None:
                        continue
                    page, line_no = str(ann[2]), int(ann[3])
                    key = (page, line_no)
                    if key in seen or key not in lookup:
                        continue
                    seen.add(key)
                    eid = f"{page}:{line_no}"
                    evidence.append({"id": eid, "content": lookup[key], "source": page, "trust_score": 1.0, "metadata": {"line": line_no}})
                    gold_ids.append(eid)
            rows.append({
                "id": f"fever_{ex.get('id')}",
                "dataset": "fever",
                "query": f"Verify the claim: {ex.get('claim', '')}",
                "references": [label],
                "evidence_clean": evidence,
                "gold_evidence_ids": gold_ids,
                "policy_label": "answer",
                "metadata": {"fever_label": label},
            })
    return stable_sample(rows, n, seed)


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(html.unescape(text).split())


def natural_questions(path: Path, n: int, seed: int) -> List[Dict]:
    """Parse simplified or original NQ JSONL conservatively.

    Records without a recoverable short answer are excluded from the open-answer
    manifest rather than assigned an invented reference.
    """
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            ex = json.loads(line)
            q = ex.get("question_text") or ex.get("question", {}).get("text")
            if not q: continue
            refs = []
            annotations = ex.get("annotations", []) or []
            tokens = ex.get("document_tokens", []) or []
            for ann in annotations:
                for sa in ann.get("short_answers", []) or []:
                    start, end = sa.get("start_token"), sa.get("end_token")
                    if isinstance(start, int) and isinstance(end, int) and tokens:
                        span = " ".join(str(t.get("token", "")) for t in tokens[start:end]).strip()
                        if span and span not in refs: refs.append(span)
            if not refs:
                continue
            doc_text = ex.get("document_text")
            if not doc_text and tokens:
                doc_text = " ".join(str(t.get("token", "")) for t in tokens)
            evidence = []
            if doc_text:
                evidence.append({
                    "id": f"{ex.get('example_id', 'unknown')}:document",
                    "content": _strip_html(doc_text),
                    "source": ex.get("document_url", "natural_questions_document"),
                    "trust_score": 1.0,
                    "metadata": {},
                })
            rows.append({
                "id": f"nq_{ex.get('example_id')}",
                "dataset": "natural_questions",
                "query": q,
                "references": refs,
                "evidence_clean": evidence,
                "gold_evidence_ids": [evidence[0]["id"]] if evidence else [],
                "policy_label": "answer",
                "metadata": {"document_url": ex.get("document_url")},
            })
    return stable_sample(rows, n, seed)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--truthfulqa", type=Path)
    p.add_argument("--fever-claims", type=Path)
    p.add_argument("--fever-evidence", type=Path)
    p.add_argument("--hotpotqa", type=Path)
    p.add_argument("--natural-questions", type=Path)
    p.add_argument("--n-per-dataset", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    all_rows = []
    if args.truthfulqa:
        all_rows.extend(truthfulqa(args.truthfulqa, args.n_per_dataset, args.seed))
    if args.hotpotqa:
        all_rows.extend(hotpotqa(args.hotpotqa, args.n_per_dataset, args.seed + 1))
    if args.fever_claims or args.fever_evidence:
        if not (args.fever_claims and args.fever_evidence):
            p.error("FEVER requires both --fever-claims and --fever-evidence")
        all_rows.extend(fever(args.fever_claims, args.fever_evidence, args.n_per_dataset, args.seed + 2))
    if args.natural_questions:
        all_rows.extend(natural_questions(args.natural_questions, args.n_per_dataset, args.seed + 3))
    if not all_rows:
        p.error("Provide at least one benchmark input.")
    write_jsonl(all_rows, args.out)
    print(f"Saved {len(all_rows)} benchmark records to {args.out}")


if __name__ == "__main__":
    main()
