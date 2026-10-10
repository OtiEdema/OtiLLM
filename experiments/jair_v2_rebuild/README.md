# OtiLLM v2.0 JAIR Evaluation Rebuild

This directory replaces the legacy JAIR evaluation scripts for publication-grade experiments.

## Design principles

1. Every reported number must be derivable from per-example raw outputs.
2. Clean and stress conditions must differ through explicit, deterministic evidence transformations.
3. Content correctness, evidence faithfulness, unsupported-claim rate, refusal behaviour, trace coverage, latency, and call/token cost are recorded separately.
4. Baselines and OtiLLM run through one harness and one manifest format.
5. No statistical value is hard-coded.
6. Missing evaluators or publication backends fail closed.

## Smoke test

The smoke backend is for pipeline verification only and must never be cited as a publication result.

```bash
python run_experiments.py --manifest data/smoke_manifest.jsonl --systems configs/systems.json --backend configs/backend_smoke.json --out results/smoke_raw.jsonl
python run_stress.py --manifest data/smoke_manifest.jsonl --systems configs/systems.json --backend configs/backend_smoke.json --out results/smoke_stress_raw.jsonl
```

## Publication run

Before a publication run:

- set the exact common backend in configs/backend.json;
- enable only systems with fully specified adapters;
- replace the smoke manifest with the archived benchmark manifest;
- configure independent factuality and claim-to-evidence evaluators;
- archive raw outputs before aggregation.

Then run:

```bash
python run_experiments.py --manifest data/jair_manifest.jsonl --systems configs/systems.json --backend configs/backend.json --out results/raw.jsonl
python run_stress.py --manifest data/jair_manifest.jsonl --systems configs/systems.json --backend configs/backend.json --out results/stress_raw.jsonl
python aggregate_results.py --input results/raw.jsonl --out results/summary.csv
python statistical_validation.py --input results/raw.jsonl --out results/statistics.csv
```

## Current implementation boundary

See IMPLEMENTATION_STATUS.md. Minimal and Full OtiLLM variants are disabled until their controller behaviour is experimentally distinct from Balanced.
