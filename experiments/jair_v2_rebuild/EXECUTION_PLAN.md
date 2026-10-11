# Publication execution plan

The frozen manifest is generated independently of model inference. The primary
model experiment requires a GPU-capable environment because the common backend
is Qwen3-8B.

## Phase A — clean content + policy evaluation

Run all eight primary systems on the frozen manifest:

```bash
python run_experiments.py \
  --manifest data/jair_manifest.jsonl \
  --systems configs/systems_publication.json \
  --backend configs/backend.json \
  --out results/raw_clean.jsonl \
  --resume
```

This includes the four content benchmarks and XSTest.

## Phase B — retrieval stress

Run only retrieval-consuming systems:

```bash
python run_stress.py \
  --manifest data/jair_manifest.jsonl \
  --systems configs/systems_stress.json \
  --backend configs/backend.json \
  --out results/raw_stress.jsonl \
  --resume
```

XSTest is excluded automatically because retrieval perturbations are not defined
for the policy-only benchmark.

## Phase C — independent scoring

Apply the pinned NLI evaluator separately to clean and stress content outputs.
XSTest rows retain policy metrics but are excluded from factuality/faithfulness
scoring.

## Phase D — statistical analysis

Aggregate per dataset first, then compute equal-weight macro averages across
TruthfulQA, FEVER, HotpotQA and Natural Questions. XSTest remains separate.

## Phase E — human validation

Select a deterministic stratified subset, blind system identity, obtain two
independent ratings, calculate raw agreement and Cohen kappa, then adjudicate
disagreements without using the adjudicated sample for threshold tuning.

## Phase F — manuscript regeneration

Only tables, figures and claims produced by these frozen outputs are eligible
for the JAIR manuscript. Legacy values remain quarantined.


## Phase A completion checkpoint

The clean publication runner is designed to produce 10,000 observations from
1,250 frozen items × 8 systems. After all deterministic shards are complete,
merge them with `merge_result_shards.py` and require exactly 10,000 unique
`(id, system, condition)` keys before any downstream scoring or manuscript
analysis.

The retrieval-stress phase now defaults to the five perturbed conditions only:
`noisy`, `contradictory`, `incomplete`, `adversarial`, and `stale`.
The clean condition is reused from Phase A rather than regenerated. With 800
content items × 4 retrieval-consuming systems × 5 perturbations, the expected
stress output is 16,000 observations.
