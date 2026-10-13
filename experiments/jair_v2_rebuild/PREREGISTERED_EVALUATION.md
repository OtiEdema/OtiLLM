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
mode. All model-based systems use the same revision and deterministic greedy
decoding (temperature 0.0) with a 256-token generation cap. Any stochastic
sensitivity analysis is reported separately from the primary results.

## Benchmark sample

Default primary manifest target: 200 records from each of TruthfulQA, FEVER,
HotpotQA and Natural Questions, selected by deterministic hash sampling with
seed 42, plus the complete 450-item XSTest suite (250 safe and 200 unsafe
contrast prompts) for refusal calibration. The frozen manifest metadata, exact counts and SHA-256 checksum supersede
these planned counts if a benchmark filter yields fewer eligible records.

## Primary outcomes

- Benchmark-native/open-answer correctness: Exact Match and token F1 as applicable.
- Independent reference factuality: pinned NLI evaluator plus human validation.
- Evidence faithfulness: claim-level entailment against the exact evidence shown.
- Unsupported-claim rate: unsupported factual claims / all factual claims.
- Refusal: precision, recall, false-refusal rate and unsafe-answer rate, evaluated primarily on XSTest.
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


## XSTest policy-path correction after diagnostic failure

The first frozen XSTest run exposed a structural confound: OtiLLM routed
evidence-free policy prompts through the same evidence-sufficiency gate used for
content QA, causing blanket abstention (all 250 safe prompts were refused, while
all 200 unsafe prompts were withheld). This was diagnosed before any revised
XSTest results were generated.

The correction is architectural and label-independent:
1. the task type `policy_refusal` is passed as runtime context;
2. static runtime policy is applied first;
3. a semantic SAFE/UNSAFE policy classifier using the same pinned model and the
   same classification instruction as the guardrail baseline is applied;
4. permitted policy-only prompts execute without requiring external evidence;
5. unsafe prompts are refused;
6. content QA and all retrieval-stress experiments retain the original
   evidence-sufficiency/confidence gates unchanged.

No XSTest gold policy label is exposed to the runtime. Only OtiLLM XSTest rows
will be regenerated because the correction does not affect content-task
execution. The original failed XSTest result remains documented as a diagnostic
limitation rather than being silently discarded.


### Corrected XSTest outcome

After the task-aware policy-path correction was implemented and frozen, OtiLLM
was rerun only on the 450 XSTest items. The corrected runtime answered 208/250
safe prompts and refused 42/250 safe prompts (safe-prompt accuracy 0.832;
false-refusal rate 0.168). It refused 197/200 unsafe prompts and answered 3/200
unsafe prompts (unsafe-prompt accuracy 0.985; unsafe-answer rate 0.015).
Overall policy correctness was therefore 405/450 = 0.900.

Because the corrected semantic SAFE/UNSAFE classifier intentionally uses the
same pinned backend and classification instruction as the guardrail baseline,
this XSTest result should be interpreted as validation that the OtiLLM runtime
now separates policy-only decisions from evidence sufficiency. It is not
evidence that OtiLLM's policy classifier outperforms the guardrail baseline.
