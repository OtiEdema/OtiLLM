# OtiLLM v2.0 JAIR evaluation plan

This file fixes the primary analysis choices before the publication benchmark run.

## Primary systems

Eight executable configurations:

1. Direct LLM
2. Prompt Chain
3. Standard RAG
4. Strong RAG
5. Self-checking LLM
6. Guardrail LLM
7. ReAct-style agent
8. OtiLLM Balanced

OtiLLM Minimal and Full are excluded from the primary comparison until their
controller behaviour is genuinely distinct in executable code.

## Common backend

Primary generator: Qwen/Qwen3-8B, pinned in configs/backend.json, non-thinking
mode. All model-based systems use the same revision, generation limits and
temperature unless a sensitivity analysis explicitly varies them.

## Benchmark sample

Default primary manifest target: 200 records from each of TruthfulQA, FEVER,
HotpotQA and Natural Questions, selected by deterministic hash sampling with
seed 42. The frozen manifest metadata, exact counts and SHA-256 checksum supersede
these planned counts if a benchmark filter yields fewer eligible records.

## Primary outcomes

- Benchmark-native/open-answer correctness: Exact Match and token F1 as applicable.
- Independent reference factuality: pinned NLI evaluator plus human validation.
- Evidence faithfulness: claim-level entailment against the exact evidence shown.
- Unsupported-claim rate: unsupported factual claims / all factual claims.
- Refusal: precision, recall, false-refusal rate and unsafe-answer rate.
- Coverage and selective accuracy.
- Common trace completeness.
- Latency, model-call count, retrieval-call count, input tokens and output tokens.

## Retrieval-stress conditions

clean, noisy, contradictory, incomplete, adversarial and stale.

Every transformed evidence set is archived in the corresponding raw output row.

## Statistical plan

The benchmark item is the primary paired statistical unit.

- 95% paired-bootstrap confidence intervals for system differences.
- Paired permutation/McNemar-style tests added where metric form permits.
- Effect sizes reported with confidence intervals.
- Multiple comparisons identified as confirmatory or exploratory.
- No statistics copied from the legacy hard-coded validation script.

## Human validation

A fixed stratified sample is double-adjudicated using HUMAN_EVALUATION_PROTOCOL.md.
System identity is blinded where feasible. Agreement is reported before
adjudication.

## Claim boundary

Architectural mechanisms listed as partial or unevaluated in
IMPLEMENTATION_STATUS.md are not described as empirically demonstrated.
