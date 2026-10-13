# Conclusion and Future Work draft — JAIR v2.0 rebuild

## 7. Conclusion and Future Work

This paper presented OtiLLM as a governed runtime for evidence-aware LLM
systems. Rather than treating generation as the default response to every
input, OtiLLM makes policy state, evidence sufficiency, confidence, provenance,
and action eligibility explicit at inference time and uses these signals to
decide whether generation should proceed, be deferred, or be refused.

The evaluation was designed to isolate runtime-control effects by holding the
underlying language model constant. Across 10,000 clean observations and
16,000 retrieval-stress observations, OtiLLM Balanced did not dominate
conventional baselines on raw clean-task accuracy. Instead, it exhibited a
different reliability profile. On clean content benchmarks it achieved
evidence faithfulness of 0.414 at 0.597 coverage. Under degraded evidence, it
reduced answer coverage and achieved statistically significant selective
faithfulness gains over Strong RAG in four of five stress conditions and over
ReAct in three of five conditions. It also improved selective factuality over
Standard RAG and ReAct in several conditions, while Strong RAG remained more
factual in multiple settings.

The policy evaluation further showed why governance signals must be separated
semantically. After correcting an implementation path that had conflated
evidence insufficiency with policy refusal, OtiLLM achieved 90.0% policy
correctness on XSTest, with a 16.8% false-refusal rate on safe prompts and a
1.5% unsafe-answer rate on unsafe prompts. These outcomes matched the dedicated
Guardrail baseline, supporting the architectural separation of policy
governance from evidence governance rather than a claim of superior policy
classification.

The central conclusion is therefore not that OtiLLM universally outperforms
RAG, agentic, or guardrail systems. The evidence instead supports a systems
claim: explicit runtime governance can make the trade-off among answer
coverage, evidence support, factuality, policy compliance, and computational
execution observable and controllable. This is particularly relevant in
settings where an unsupported answer may be more costly than a deferred one.

Several directions remain open. First, the current confidence rule is a fixed
implementation heuristic; future work should investigate learned and calibrated
confidence models that optimise coverage and reliability jointly. Second,
retrieval reconsideration should be integrated directly into the validated
publication runtime so that insufficient evidence can trigger adaptive
re-retrieval rather than immediate deferral. Third, stronger contradiction
detection and evidence-quality estimation may improve factuality without
discarding the observed faithfulness benefits. Fourth, future work should
evaluate distinct Minimal, Balanced, and Full policies only after their
controller behaviour is genuinely different in executable code.

A further direction is longitudinal governance. The present experiments record
bounded memory-write decisions but do not establish long-term memory quality,
memory contamination resistance, causal memory effects, or policy adaptation
across sessions. These behaviours require dedicated multi-session experiments.
Similarly, the current stress suite uses controlled perturbations and should be
extended to naturally occurring source conflict, retrieval drift, adversarial
knowledge-base contamination, and domain-specific evidence pipelines.

Finally, future evaluation should examine the human and operational cost of
abstention. The desirable operating point for a governed runtime depends on the
relative cost of an incorrect answer, an unsupported answer, and a deferred
answer. Domain-specific utility studies, calibrated selective-risk curves, and
end-user evaluation would therefore provide a stronger basis for choosing
runtime thresholds than accuracy alone.

OtiLLM should thus be viewed as an initial implementation of a broader Governed
Runtime Intelligence perspective: LLM applications can be treated as
state-aware systems in which generation is one governed action among several,
rather than an unconditional endpoint. The present results provide evidence
that this shift in abstraction changes measurable system behaviour under
evidence degradation and policy constraints, while also exposing the remaining
challenge of balancing reliability against useful coverage.
