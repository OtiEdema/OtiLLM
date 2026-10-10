# Frozen JAIR v2.0 benchmark manifest

The primary benchmark manifest was successfully built and validated in GitHub
Actions run **38033877003** on 2026-10-10.

## Frozen composition

- TruthfulQA: 200
- FEVER: 200
- HotpotQA: 200
- Natural Questions: 200
- XSTest: 450
  - safe: 250
  - unsafe: 200
- Total records: 1,250

## Integrity

- Manifest SHA-256:
  `55ffbb306cd647986d92638ba326756bc91f9de3c3dafcfcc6dcec17fd988fda`
- Ordered item-ID list SHA-256:
  `ed9aac76d0529f736dcfe8265374d3919169f5102d7f6d6d76f1207f6e162c85`

The manifest passed dataset-specific validation before freezing. Publication
experiments must use a manifest with the exact manifest SHA-256 above. If a
locally regenerated manifest does not match this hash, do not run the primary
evaluation until the discrepancy is resolved.
