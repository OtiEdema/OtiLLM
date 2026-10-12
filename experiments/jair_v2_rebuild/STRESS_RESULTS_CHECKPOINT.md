# JAIR v2.0 stress-results checkpoint

Phase B (retrieval-stress evaluation) has completed structurally.

## Expected final counts

- Retrieval-consuming systems: 4
- Perturbation conditions: 5
- Content benchmark items: 800
- Expected stress observations: 16,000

Observed aggregate balance:
- standard_rag: 4,000
- strong_rag: 4,000
- react_agent: 4,000
- otillm_balanced: 4,000

Per condition:
- noisy: 3,200
- contradictory: 3,200
- incomplete: 3,200
- adversarial: 3,200
- stale: 3,200

Per dataset:
- TruthfulQA: 4,000
- FEVER: 4,000
- HotpotQA: 4,000
- Natural Questions: 4,000

The merged-file row count, uniqueness check, and SHA-256 should be recorded
after shard merge validation.
