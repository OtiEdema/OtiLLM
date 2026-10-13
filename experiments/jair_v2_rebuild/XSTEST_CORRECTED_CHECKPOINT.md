# Corrected XSTest checkpoint

The initial OtiLLM XSTest result exposed a structural confound: policy-only
prompts were routed through the evidence-sufficiency gate, causing blanket
abstention. The policy-only path was corrected before regenerating XSTest
results, without exposing gold labels to the runtime.

## Corrected OtiLLM XSTest outcome

- Safe prompts: 250
- Safe prompts answered: 208
- Safe prompts refused: 42
- Safe-prompt accuracy: 0.832
- False-refusal rate: 0.168

- Unsafe prompts: 200
- Unsafe prompts refused: 197
- Unsafe prompts answered: 3
- Unsafe-prompt accuracy: 0.985
- Unsafe-answer rate: 0.015

- Overall policy correctness: 0.900 (405/450)

## Paired policy statistics

OtiLLM policy correctness (0.900) significantly exceeds the non-policy-aware
baselines, each at 0.555556, with Holm-adjusted p = 2.419663e-24.

Against the dedicated guardrail baseline, OtiLLM is identical on:
- overall policy correctness: 0.900 vs 0.900;
- false-refusal rate on safe prompts: 0.168 vs 0.168;
- unsafe-answer rate on unsafe prompts: 0.015 vs 0.015.

McNemar p = 1.0 for all three OtiLLM-versus-guardrail comparisons.

Interpretation: the corrected OtiLLM runtime successfully separates policy-only
governance from evidence sufficiency and achieves policy behaviour equivalent
to the dedicated guardrail baseline. This does not support a claim that the
OtiLLM semantic policy classifier outperforms that baseline, because the
classification backend and instruction are intentionally shared for fairness.
