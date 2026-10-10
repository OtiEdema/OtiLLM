"""Prepare the frozen JAIR manifest directly from canonical Hugging Face datasets.

This is the preferred acquisition path for the publication rebuild. It uses
deterministic hash-based sampling so selection does not depend on row order.
Large corpora are streamed where practical.

FEVER evidence resolution is deliberately explicit: claims are sampled first,
then only the required Wikipedia pages/sentences are retained from the official
FEVER wiki-pages configuration.
"""

import argparse
import hashlib
import heapq
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from datasets import load_dataset


def rank_key(namespace: str, item_id: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}|{namespace}|{item_id}".encode("utf-8")).hexdigest()


def take_hash_sample(rows: Iterable[Dict], n: int, namespace: str, seed: int, id_fn) -> List[Dict]:
    ranked: List[Tuple[str, Dict]] = []
    for row in rows:
        rid = str(id_fn(row))
        ranked.append((rank_key(namespace, rid, seed), row))
    ranked.sort(key=lambda x: x[0])
    return [r for _, r in ranked[:n]]


def take_streaming_hash_sample(rows: Iterable[Dict], n: int, namespace: str, seed: int, id_fn, eligible_fn=None) -> List[Dict]:
    """Keep only the n smallest deterministic hash keys while streaming.

    This avoids retaining full Natural Questions documents for every validation
    record in memory.
    """
    if n <= 0:
        return []
    heap = []
    for row in rows:
        if eligible_fn is not None and not eligible_fn(row):
            continue
        rid = str(id_fn(row))
        key = rank_key(namespace, rid, seed)
        # Max-heap via negative integer hash; keep n smallest hashes.
        score = int(key, 16)
        item = (-score, rid, row)
        if len(heap) < n:
            heapq.heappush(heap, item)
        elif item[0] > heap[0][0]:
            heapq.heapreplace(heap, item)
    selected = [(-neg, rid, row) for neg, rid, row in heap]
    selected.sort(key=lambda x: x[0])
    return [row for _, _, row in selected]


def truthfulqa(n: int, seed: int) -> List[Dict]:
    ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
    sample = take_hash_sample(ds, n, "truthfulqa", seed, lambda r: r["question"])
    out = []
    for i, r in enumerate(sample):
        refs = [r["best_answer"]] + [x for x in r.get("correct_answers", []) if x != r["best_answer"]]
        out.append({
            "id": f"truthfulqa_{hashlib.sha1(r['question'].encode()).hexdigest()[:12]}",
            "dataset": "truthfulqa",
            "query": r["question"],
            "references": refs,
            "evidence_clean": [],
            "gold_evidence_ids": [],
            "policy_label": "answer",
            "metadata": {
                "category": r.get("category"),
                "type": r.get("type"),
                "source": r.get("source"),
                "benchmark_native_evidence": False,
            },
        })
    return out


def hotpotqa(n: int, seed: int) -> List[Dict]:
    ds = load_dataset("hotpotqa/hotpot_qa", "distractor", split="validation")
    sample = take_hash_sample(ds, n, "hotpotqa", seed, lambda r: r["id"])
    out = []
    for r in sample:
        sf_titles = list(r["supporting_facts"]["title"])
        sf_ids = list(r["supporting_facts"]["sent_id"])
        gold = set(zip(sf_titles, sf_ids))
        evidence, gold_ids = [], []
        titles = list(r["context"]["title"])
        sentence_lists = list(r["context"]["sentences"])
        for title, sentences in zip(titles, sentence_lists):
            for sid, sent in enumerate(sentences):
                eid = f"{r['id']}::{title}::{sid}"
                evidence.append({
                    "id": eid,
                    "content": sent,
                    "source": title,
                    "trust_score": 1.0,
                    "metadata": {"title": title, "sentence_id": sid},
                })
                if (title, sid) in gold:
                    gold_ids.append(eid)
        out.append({
            "id": f"hotpotqa_{r['id']}",
            "dataset": "hotpotqa",
            "query": r["question"],
            "references": [str(r["answer"])],
            "evidence_clean": evidence,
            "gold_evidence_ids": gold_ids,
            "policy_label": "answer",
            "metadata": {"type": r.get("type"), "level": r.get("level")},
        })
    return out


def nq_short_answers(record: Dict) -> List[str]:
    refs = []
    annotations = record.get("annotations", [])
    # Converted HF schema may be list-of-dicts or dict-of-lists.
    if isinstance(annotations, dict):
        sa = annotations.get("short_answers", [])
        if isinstance(sa, dict):
            for text in sa.get("text", []) or []:
                if isinstance(text, list):
                    for t in text:
                        if t and t not in refs:
                            refs.append(t)
                elif text and text not in refs:
                    refs.append(text)
        elif isinstance(sa, list):
            annotations = [{"short_answers": sa}]
    if isinstance(annotations, list):
        for ann in annotations:
            sa = ann.get("short_answers", [])
            if isinstance(sa, dict):
                texts = sa.get("text", []) or []
                for t in texts:
                    if isinstance(t, list):
                        for tt in t:
                            if tt and tt not in refs:
                                refs.append(tt)
                    elif t and t not in refs:
                        refs.append(t)
            else:
                for x in sa or []:
                    t = x.get("text") if isinstance(x, dict) else None
                    if t and t not in refs:
                        refs.append(t)
    return refs


def natural_questions(n: int, seed: int) -> List[Dict]:
    # Stream validation to avoid materialising the large document corpus.
    ds = load_dataset(
        "google-research-datasets/natural_questions",
        "default",
        split="validation",
        streaming=True,
    )
    sample = take_streaming_hash_sample(
        ds,
        n,
        "natural_questions",
        seed,
        lambda r: r["id"],
        eligible_fn=lambda r: bool(nq_short_answers(r)),
    )

    out = []
    for r in sample:
        refs = nq_short_answers(r)
        doc = r.get("document", {}) or {}
        tokens = doc.get("tokens", []) or []
        if isinstance(tokens, dict):
            tok_text = tokens.get("token", []) or []
            is_html = tokens.get("is_html", []) or [False] * len(tok_text)
            clean_tokens = [t for t, h in zip(tok_text, is_html) if not h]
        else:
            clean_tokens = [x.get("token", "") for x in tokens if not x.get("is_html", False)]
        evidence_text = " ".join(t for t in clean_tokens if t).strip()
        eid = f"{r['id']}::document"
        evidence = [{
            "id": eid,
            "content": evidence_text,
            "source": doc.get("url") or doc.get("title") or "natural_questions_document",
            "trust_score": 1.0,
            "metadata": {"title": doc.get("title"), "url": doc.get("url")},
        }] if evidence_text else []
        q = r.get("question", {})
        query = q.get("text") if isinstance(q, dict) else str(q)
        out.append({
            "id": f"nq_{r['id']}",
            "dataset": "natural_questions",
            "query": query,
            "references": refs,
            "evidence_clean": evidence,
            "gold_evidence_ids": [eid] if evidence else [],
            "policy_label": "answer",
            "metadata": {"document_url": doc.get("url"), "document_title": doc.get("title")},
        })
    return out


def parse_fever_lines(lines: str) -> Dict[int, str]:
    result = {}
    for raw in (lines or "").splitlines():
        parts = raw.split("\t", 1)
        if not parts:
            continue
        try:
            idx = int(parts[0])
        except ValueError:
            continue
        result[idx] = parts[1] if len(parts) > 1 else ""
    return result


def fever(n: int, seed: int) -> List[Dict]:
    """Build a deterministic FEVER sample with resolvable gold evidence.

    We oversample candidate claims before resolving Wikipedia pages. This avoids
    failing the entire frozen build when a small number of legacy FEVER evidence
    page identifiers cannot be resolved from the mirrored wiki-pages corpus.
    """
    claims = load_dataset(
        "EleutherAI/fever", "v1.0", split="dev", trust_remote_code=True
    )

    grouped = {}
    for r in claims:
        cid = str(r["id"])
        g = grouped.setdefault(
            cid,
            {"id": cid, "claim": r["claim"], "label": r["label"], "evidence": []},
        )
        page = str(r.get("evidence_wiki_url") or "")
        sent = int(r.get("evidence_sentence_id", -1))
        if page and sent >= 0:
            g["evidence"].append((page, sent))

    # Deterministically oversample so unresolved legacy page ids can be skipped
    # without changing the sampling rule after observing model outputs.
    rows = list(grouped.values())
    pool_n = min(len(rows), max(n + 50, int(n * 1.5)))
    selected_pool = take_hash_sample(
        rows, pool_n, "fever", seed, lambda r: r["id"]
    )

    wanted_pages = set(
        page for r in selected_pool for page, _ in r["evidence"]
    )
    page_lines: Dict[str, Dict[int, str]] = {}
    unresolved_pages = set(wanted_pages)

    if wanted_pages:
        wiki = load_dataset(
            "EleutherAI/fever",
            "wiki_pages",
            split="wikipedia_pages",
            streaming=True,
            trust_remote_code=True,
        )
        for page in wiki:
            pid = str(page["id"])
            if pid in unresolved_pages:
                page_lines[pid] = parse_fever_lines(page.get("lines", ""))
                unresolved_pages.remove(pid)
                if not unresolved_pages:
                    break

    out = []
    skipped_unresolved = []
    for r in selected_pool:
        evidence, gold_ids, seen = [], [], set()
        unresolved_claim_evidence = False

        for page, sent in r["evidence"]:
            key = (page, sent)
            if key in seen:
                continue
            seen.add(key)
            text = page_lines.get(page, {}).get(sent, "")
            if not text:
                unresolved_claim_evidence = True
                continue
            eid = f"{page}::{sent}"
            evidence.append({
                "id": eid,
                "content": text,
                "source": page,
                "trust_score": 1.0,
                "metadata": {"sentence_id": sent},
            })
            gold_ids.append(eid)

        label = r["label"]
        # SUPPORTS/REFUTES claims need at least one resolved gold evidence
        # sentence for the evidence-grounded evaluation. NEI claims legitimately
        # have no gold supporting evidence.
        if label != "NOT ENOUGH INFO" and not gold_ids:
            skipped_unresolved.append(r["id"])
            continue

        out.append({
            "id": f"fever_{r['id']}",
            "dataset": "fever",
            "query": (
                "Verify the claim and answer SUPPORTS, REFUTES, or NOT ENOUGH INFO: "
                + r["claim"]
            ),
            "references": [label],
            "evidence_clean": evidence,
            "gold_evidence_ids": gold_ids,
            "policy_label": "answer",
            "metadata": {
                "fever_label": label,
                "benchmark_native_evidence": bool(gold_ids),
                "evidence_resolution_complete": not unresolved_claim_evidence,
            },
        })
        if len(out) == n:
            break

    if len(out) < n:
        raise RuntimeError(
            f"FEVER produced only {len(out)} eligible records after evidence "
            f"resolution; requested {n}. Increase the deterministic candidate pool."
        )

    if skipped_unresolved:
        print(
            f"fever_skipped_unresolved_claims={len(skipped_unresolved)} "
            f"unresolved_pages={len(unresolved_pages)}"
        )
    return out

def xstest(seed: int) -> List[Dict]:
    """Load the complete XSTest suite for refusal calibration.

    XSTest contains 250 safe prompts and 200 unsafe contrast prompts. The full
    450-item test suite is retained because it is small and specifically designed
    to measure both exaggerated safety and under-refusal.
    """
    ds = load_dataset("walledai/XSTest", split="test")
    out = []
    for idx, r in enumerate(ds):
        label = str(r.get("label", "")).strip().lower()
        if label not in {"safe", "unsafe"}:
            continue
        prompt = r.get("prompt")
        if not prompt:
            continue
        out.append({
            "id": f"xstest_{idx:04d}",
            "dataset": "xstest",
            "query": prompt,
            # References are retained only to satisfy the common manifest schema;
            # answer correctness metrics are disabled for this policy benchmark.
            "references": [label.upper()],
            "evidence_clean": [],
            "gold_evidence_ids": [],
            "policy_label": "answer" if label == "safe" else "refuse",
            "metadata": {
                "xstest_label": label,
                "type": r.get("type"),
                "focus": r.get("focus"),
                "note": r.get("note"),
                "task_type": "policy_refusal",
            },
        })
    # Stable order independent of upstream row order.
    return sorted(
        out,
        key=lambda r: rank_key("xstest", r["query"], seed),
    )


def write_jsonl(rows: Sequence[Dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-per-dataset", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--datasets", nargs="+", default=["truthfulqa", "fever", "hotpotqa", "natural_questions", "xstest"])
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    builders = {
        "truthfulqa": truthfulqa,
        "fever": fever,
        "hotpotqa": hotpotqa,
        "natural_questions": natural_questions,
        "xstest": lambda _n, s: xstest(s),
    }
    rows = []
    for offset, name in enumerate(args.datasets):
        if name not in builders:
            p.error(f"Unknown dataset {name!r}")
        built = builders[name](args.n_per_dataset, args.seed + offset)
        rows.extend(built)
        print(f"{name}: {len(built)}")

    write_jsonl(rows, args.out)
    print(f"Saved {len(rows)} records to {args.out}")


if __name__ == "__main__":
    main()
