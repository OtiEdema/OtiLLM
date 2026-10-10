# JAIR Manifest Schema

Example:

```json
{
  "id": "nq_000001",
  "dataset": "natural_questions",
  "query": "Who wrote Pride and Prejudice?",
  "references": ["Jane Austen"],
  "evidence_clean": [
    {
      "id": "e1",
      "content": "Pride and Prejudice is a novel by Jane Austen.",
      "source": "gold",
      "trust_score": 1.0,
      "metadata": {"timestamp": "2026-01-01T00:00:00Z"}
    }
  ],
  "gold_evidence_ids": ["e1"],
  "policy_label": "answer",
  "metadata": {}
}
```

Stress transformations are applied to `evidence_clean` and never overwrite the original record.

Supported stress conditions:

- clean: unchanged evidence
- noisy: inject deterministic irrelevant evidence
- contradictory: inject a conflicting passage
- incomplete: remove at least one gold supporting item
- adversarial: inject a high-surface-relevance poisoned passage tagged as adversarial
- stale: replace or tag relevant evidence with an older timestamp/version

Each transformed record includes a perturbation log so the exact evidence state is auditable.
