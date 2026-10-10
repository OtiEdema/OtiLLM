# JAIR v2.0 empirical release checklist

A manuscript result is publication-ready only when all applicable boxes are checked.

## Dataset
- [ ] Exact benchmark versions documented.
- [ ] Licences/terms checked.
- [ ] Item IDs archived.
- [ ] Reference answers archived or reproducibly resolvable.
- [ ] Clean evidence corpus/version archived.
- [ ] Policy labels independently reviewed.
- [ ] No test-set contamination introduced by evaluation prompts.

## Systems
- [ ] Exact common model backend named.
- [ ] Model/version snapshot or date documented.
- [ ] Temperature, max tokens and context limits fixed.
- [ ] Baseline prompts archived.
- [ ] Retrieval parameters identical where comparison requires parity.
- [ ] OtiLLM implementation-status table matches executable code.
- [ ] v2.0 publication tag/version is consistent in code, README and manuscript.

## Metrics
- [ ] Benchmark-native answer metric.
- [ ] Independent factuality evaluator.
- [ ] Claim-to-evidence faithfulness evaluator.
- [ ] Unsupported-claim rate computed from claims, not as 1-faithfulness.
- [ ] Refusal precision/recall/false-refusal/unsafe-answer/coverage.
- [ ] Common trace schema applied to all systems.
- [ ] Latency recorded.
- [ ] LLM and retrieval call counts recorded.
- [ ] Token/cost data recorded when backend exposes them.

## Stress evaluation
- [ ] Clean.
- [ ] Noisy.
- [ ] Contradictory.
- [ ] Incomplete.
- [ ] Adversarial.
- [ ] Stale.
- [ ] Every perturbation logged per example.
- [ ] Human spot-check of transformed evidence.

## Statistics
- [ ] Per-example raw outputs archived.
- [ ] Paired comparisons use common example IDs.
- [ ] Bootstrap confidence intervals.
- [ ] Multiple-comparison policy documented.
- [ ] No hard-coded p-values/effect sizes.
- [ ] Seeds recorded.
- [ ] Sensitivity analysis over thresholds.

## Reproducibility
- [ ] One-command run instructions.
- [ ] Environment lockfile.
- [ ] Exact git commit/tag.
- [ ] Figure regeneration from raw outputs.
- [ ] Tables generated from raw outputs.
- [ ] JAIR reproducibility checklist completed.
