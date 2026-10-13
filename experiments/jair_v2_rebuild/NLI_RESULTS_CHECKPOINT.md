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

Merged scored files and SHA-256 values should be recorded after merge validation.
