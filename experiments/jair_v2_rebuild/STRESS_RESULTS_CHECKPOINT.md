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

Merged-file validation:
- Rows: 16,000
- Unique keys: 16,000
- Duplicate keys: 0
- Merged file size: 86.79 MB
- Merged stress-results SHA-256:
  `6722c132188e02db5c4bd0647475542e7f795b38fd6bbfe4f79e2d6524e63098`

This checksum is the authoritative Phase B merged-result integrity value for
the JAIR v2.0 rebuild. Downstream scoring and statistical analysis should use
this merged file or a byte-identical copy.
