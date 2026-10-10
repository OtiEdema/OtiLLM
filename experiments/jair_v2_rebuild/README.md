# OtiLLM v2.0 JAIR Evaluation Rebuild

This directory replaces the legacy JAIR evaluation scripts for publication-grade experiments.

## Design principles

1. Every reported number must be derivable from per-example raw outputs.
2. Clean and stress conditions must differ through explicit, deterministic evidence transformations.
3. Content correctness, evidence faithfulness, unsupported-claim rate, refusal behaviour, trace coverage, latency, and call/token cost are recorded separately.
4. Baselines and OtiLLM variants run through one harness and one manifest format.
5. No statistical value is hard-coded. Confidence intervals and paired tests are computed from raw observations.
6. Missing evaluators fail closed: the pipeline does not silently substitute a weak proxy for a stronger construct.

## Required manifest fields

Each JSONL record must include:

- id
- dataset
- query
- references: list of acceptable reference answers
- evidence_clean: list of evidence objects with content, source, trust_score and optional metadata
- gold_evidence_ids: optional list of supporting evidence ids
- policy_label: one of answer, refuse, defer
- metadata: optional benchmark metadata

See data/SCHEMA.md.

## Recommended run order

```bash
python run_experiments.py --manifest data/jair_manifest.jsonl --systems configs/systems.json --out results/raw.jsonl
python run_stress.py --manifest data/jair_manifest.jsonl --systems configs/systems.json --out results/stress_raw.jsonl
python aggregate_results.py --input results/raw.jsonl --out results/summary.csv
python aggregate_results.py --input results/stress_raw.jsonl --out results/stress_summary.csv
python statistical_validation.py --input results/raw.jsonl --out results/statistics.csv
```

## Publication rule

Do not transfer any result into the manuscript unless it can be regenerated from the archived raw JSONL with the scripts in this directory.

## Current implementation boundary

The current public OtiLLM runtime implements policy gating, retrieval, evidence sufficiency, confidence gating, execution/defer, memory write gating and structured runtime traces. Some formal actions described in the paper remain architectural specifications rather than fully realised v2.0 mechanisms. The manuscript must preserve this boundary.
