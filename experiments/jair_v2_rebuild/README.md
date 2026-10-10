# OtiLLM v2.0 JAIR Evaluation Rebuild

This directory replaces the legacy JAIR evaluation scripts for publication-grade experiments.

## Design principles

1. Every reported number must be derivable from per-example raw outputs.
2. Clean and stress conditions must differ through explicit, deterministic evidence transformations.
3. Content correctness, evidence faithfulness, unsupported-claim rate, refusal behaviour, trace coverage, latency, and call/token cost are recorded separately.
4. Baselines and OtiLLM run through one harness and one manifest format.
5. No statistical value is hard-coded.
6. Missing evaluators or publication backends fail closed.


## Build and freeze the real benchmark manifest

Install evaluation dependencies, then construct the deterministic manifest from
canonical Hugging Face datasets:

```bash
python -m pip install -r requirements-eval.txt

python prepare_hf_manifest.py \
  --n-per-dataset 200 \
  --seed 42 \
  --datasets truthfulqa fever hotpotqa natural_questions \
  --out data/jair_manifest.jsonl

python validate_manifest.py data/jair_manifest.jsonl

python freeze_manifest.py data/jair_manifest.jsonl \
  --seed 42 \
  --metadata-out data/jair_manifest.metadata.json
```

The frozen metadata file records the manifest SHA-256, exact dataset counts,
item-ID checksum, git commit and branch. The manuscript must use those frozen
counts rather than planned sample sizes.

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
python run_experiments.py --manifest data/jair_manifest.jsonl --systems configs/systems_publication.json --backend configs/backend.json --out results/raw.jsonl
python run_stress.py --manifest data/jair_manifest.jsonl --systems configs/systems.json --backend configs/backend.json --out results/stress_raw.jsonl
python aggregate_results.py --input results/raw.jsonl --out results/summary.csv
python statistical_validation.py --input results/raw.jsonl --out results/statistics.csv
```

## Current implementation boundary

See IMPLEMENTATION_STATUS.md. Minimal and Full OtiLLM variants are disabled until their controller behaviour is experimentally distinct from Balanced.

## Independent scoring

After generation, attach claim-level factuality and evidence-faithfulness scores with the pinned NLI evaluator:

```bash
python score_outputs.py \
  --raw results/raw.jsonl \
  --manifest data/jair_manifest.jsonl \
  --nli-model MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli \
  --nli-revision 6f5cf0a2b59cabb106aca4c287eed12e357e90eb \
  --threshold 0.5 \
  --out results/raw_scored.jsonl
```

For stress outputs, use the corresponding stress JSONL. Each stress row archives the exact transformed evidence exposed to the system so faithfulness is evaluated against the actual condition, not the clean corpus.

Then generate a blinded human-adjudication sheet from a fixed stratified sample. Automated NLI scores are treated as one evaluator, not as ground truth.
