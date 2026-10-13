# JAIR v2.0 independent NLI-scoring checkpoint

Independent NLI scoring has completed structurally for both clean and stress outputs.

## Evaluator

- Model: MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli
- Revision: 6f5cf0a2b59cabb106aca4c287eed12e357e90eb
- Entailment threshold: 0.5
- Device: CUDA when available
- Metrics: reference factuality and evidence faithfulness

## Clean scoring

- Expected observations: 10,000
- Observed observations: 10,000
- Unique global keys: 10,000
- Duplicate keys: 0

## Stress scoring

- Expected observations: 16,000
- Observed observations: 16,000
- Unique global keys: 16,000
- Duplicate keys: 0

## Merged scored files

Clean merged scoring:
- Rows: 10,000
- Unique keys: 10,000
- Duplicate keys: 0
- Size: 18.38 MB
- SHA-256: `f22c3514b651d413b972125e4a577e6bb7733aa006deb2f3783852532b3b7f5c`

Stress merged scoring:
- Rows: 16,000
- Unique keys: 16,000
- Duplicate keys: 0
- Size: 101.39 MB
- SHA-256: `ae678a2fdb381b0ebfaff06b3e81bb68cbdcb2d9d4bcf39fcb4f8e250bcec7c5`

These checksums are the authoritative merged NLI-scored result integrity
values for downstream analysis in the JAIR v2.0 rebuild.
