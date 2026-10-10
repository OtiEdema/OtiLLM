# Frozen JAIR v2.0 benchmark manifest

The corrected primary benchmark manifest was successfully built, validated,
frozen and uploaded by GitHub Actions run **38038548943** on 2026-10-10.

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
  `62bd9c4b6bf8810a93a2065683f4d29a3f946246a45f2b1be98c6459e18b329c`
- Ordered item-ID list SHA-256:
  `ed9aac76d0529f736dcfe8265374d3919169f5102d7f6d6d76f1207f6e162c85`

The ordered item-ID checksum is unchanged from the superseded build, confirming
that the same deterministic 1,250 sampled items are retained. The manifest
content checksum changed because FEVER ClassLabel ids are now decoded to
textual SUPPORTS/REFUTES labels and Natural Questions short-answer references
are flattened to scalar strings.

The earlier manifest SHA-256
`55ffbb306cd647986d92638ba326756bc91f9de3c3dafcfcc6dcec17fd988fda`
is superseded and must not be used for publication evaluation.

Publication experiments must use a manifest with the exact corrected SHA-256
above. If a locally regenerated manifest does not match, stop before running
the primary evaluation and resolve the discrepancy.
