# Full Manuscript Consistency Audit — JAIR v2.0 Rebuild

## Executive assessment

The rebuilt manuscript now has a coherent central claim: OtiLLM is a governed
runtime layer that makes evidence sufficiency, policy state, confidence, and
execution eligibility explicit, trading coverage for conditional reliability
rather than universally maximising raw accuracy.

Across the current Abstract/Introduction, Related Work/Architecture,
Methodology, Results, and Discussion drafts, the principal empirical story is
consistent. However, several issues should be resolved before the manuscript is
treated as submission-ready. The most important outstanding issue is human
validation of the automated NLI-based factuality and faithfulness scores.

## A. Claim consistency

### A1. Core claim — consistent

The manuscript consistently avoids a universal superiority claim. The supported
position is:

> OtiLLM changes the reliability profile of a common LLM through explicit
> runtime governance, selectively abstaining under weak evidence and improving
> conditional evidence faithfulness in several degraded-evidence settings.

This wording is compatible with the clean, stress, and XSTest results.

### A2. Claims that must remain prohibited

The following claims are not supported by the current evidence and should not
appear anywhere in the final manuscript:

- OtiLLM universally outperforms RAG.
- OtiLLM is the most factual system.
- OtiLLM is the safest system.
- OtiLLM introduces a superior safety classifier.
- OtiLLM fully implements all aspects of Governed Runtime Intelligence.
- Retrieval Reconsideration Dynamics is fully validated.
- Cognitive Utility Optimisation is fully validated.
- Governed Cognitive Memory is longitudinally validated.
- Minimal, Balanced, and Full modes have all been experimentally compared.
- ReAct in this paper represents unrestricted autonomous agentic retrieval.
- Synthetic contradictory/adversarial evidence represents the complete
  distribution of real-world misinformation or poisoning.

## B. Cross-section numerical consistency

The following headline values are consistent across the current drafts and
should be treated as canonical unless later human validation changes their
interpretation:

- total clean observations: 10,000;
- total stress observations: 16,000;
- total system-level observations: 26,000;
- clean OtiLLM content coverage: 0.597;
- clean OtiLLM faithfulness: 0.414;
- clean OtiLLM factuality: 0.230;
- clean unsupported-claim rate: 0.586;
- clean latency: 2.713 s;
- clean faithfulness relative to Direct LLM: +29.4%;
- clean unsupported-claim-rate reduction relative to Direct LLM: 13.8%;
- XSTest policy correctness: 0.900 (405/450);
- safe-prompt false-refusal rate: 0.168 (42/250);
- unsafe-prompt unsafe-answer rate: 0.015 (3/200).

The stress significance claims are also internally consistent:
- selective faithfulness > Strong RAG in 4/5 conditions;
- selective faithfulness > ReAct in 3/5 conditions;
- selective factuality > Standard RAG in 4/5 conditions;
- selective factuality > ReAct in 3/5 conditions;
- Strong RAG remains significantly more factual in several conditions.

## C. Research-question audit

The current RQ1 and RQ2 are well aligned with the design and results.

RQ3 is somewhat too tightly coupled to the post-diagnostic XSTest correction:

> Can policy-only execution be separated from evidence-sufficiency gating...?

For final submission, a less post-hoc formulation is preferable:

> **RQ3. How does task-aware policy gating affect refusal correctness, false
> refusals, and unsafe answers when external evidence is not required for the
> task?**

This still matches the XSTest evaluation while reducing the appearance that
the research question was written around the observed implementation defect.

## D. Architecture audit

The architecture section correctly distinguishes the broader OtiLLM vision
from the publication runtime. This distinction should be retained.

The final paper should explicitly label the following two layers:

1. **Validated publication runtime** — evidence retrieval/scoring,
   evidence-sufficiency gating, policy gating, confidence gating,
   execute/defer/refuse behaviour, bounded memory-write gating, and structured
   operational trace.
2. **Broader architectural extensions** — full Retrieval Reconsideration
   Dynamics, formal Cognitive Utility Optimisation, clarification/escalation/
   forget actions, longitudinal Governed Cognitive Memory, learned controller,
   and distinct Minimal/Balanced/Full policies.

This prevents architecture diagrams from visually implying that all modules
were evaluated.

## E. Methodology audit

The revised methodology substantially improves reproducibility and should
retain:

- Google Colab cloud execution environment;
- NVIDIA L4 GPU;
- approximately 48 hours of cumulative execution and validation;
- deterministic sharding;
- Google Drive persistence/checkpointing;
- frozen manifest and result checksums;
- fixed Qwen3-8B revision;
- fixed independent NLI revision;
- clean/stress separation;
- paired selective analysis;
- bootstrap/permutation/McNemar tests;
- Holm correction;
- transparent XSTest correction.

Two refinements are recommended:

### E1. Hardware reporting

Report the L4 GPU as part of reproducibility, not as a performance claim.
Where available, add the actual runtime software versions used in the final
Colab run (Python, PyTorch, Transformers, CUDA visible to PyTorch). Do not infer
versions that were not recorded.

### E2. XSTest correction placement

Keep a concise disclosure in the main methodology, but move the full chronology
and original failed diagnostic values to an appendix or reproducibility note.
This keeps the main paper readable while preserving complete transparency.

## F. Major outstanding validity issue: human validation

The current automated factuality and faithfulness results rely on a pinned
DeBERTa NLI evaluator. The manuscript itself correctly states that this
evaluator is not ground truth and that a stratified human adjudication stage is
required.

**This remains the most important outstanding experiment before submission.**

Until human validation is completed, the paper should use phrasing such as:

> automated NLI-based factuality estimate

and:

> automated evidence-faithfulness estimate

for the primary semantic metrics, rather than presenting them as unquestioned
ground truth.

The human-validation stage should report at least:
- fixed stratified sample design;
- two independent adjudicators;
- blinded system identity where feasible;
- correctness/factuality judgement;
- evidence-support/faithfulness judgement;
- refusal appropriateness where applicable;
- inter-rater agreement;
- Cohen's kappa or another suitable agreement statistic;
- adjudicated final labels;
- correlation/agreement between human and NLI-based scores.

If human validation materially disagrees with the NLI evaluator, the final
claims must be revised accordingly.

## G. Related-work audit

The current Related Work is directionally correct but still too compact for a
strong JAIR submission. It should be expanded before finalisation.

The final literature review should contain a stronger comparison with:
- foundational and adaptive RAG;
- retrieval reliability and retrieval robustness;
- self-verification / self-reflection;
- selective prediction and abstention;
- uncertainty-aware LLM systems;
- hallucination and faithfulness evaluation;
- guardrails and runtime safety;
- agent/tool orchestration;
- memory governance and persistent agents;
- provenance and auditability;
- relevant JAIR work, especially where conceptually adjacent.

The paper should make clear that Governed Runtime Intelligence is an integrative
systems abstraction and not a claim that individual components such as
retrieval, refusal, memory, or tracing are themselves novel.

All references currently written in author-year prose must be verified and
converted to the exact JAIR bibliography format in the final source.

## H. Results audit

The Results section is statistically cautious and mostly well aligned.

Recommended final presentation:

- Table 1: benchmark composition and system definitions.
- Table 2: clean content macro results.
- Table 3: stress coverage by condition.
- Table 4: paired selective faithfulness results.
- Table 5: paired selective factuality results.
- Table 6: XSTest policy outcomes.
- Figure 1: OtiLLM governed runtime architecture.
- Figure 2: experimental/reproducibility pipeline.
- Figure 3: coverage versus selective faithfulness under stress.
- Figure 4: coverage versus selective factuality under stress.
- Figure 5: XSTest false-refusal / unsafe-answer trade-off.

Avoid placing every pairwise p-value in prose. Use the prose for the main
patterns and tables for complete statistics.

## I. Discussion audit

The Discussion is aligned with the evidence and should retain the distinction
between factuality and faithfulness.

One wording refinement is recommended. Avoid saying that lower coverage is
inherently successful governance. The paper should consistently say it is a
trade-off whose desirability depends on the cost of abstention versus the cost
of unsupported answers.

## J. Terminology consistency

Use these terms consistently throughout:

- **OtiLLM Balanced** for the evaluated system;
- **OtiLLM** when referring to the broader runtime/framework;
- **governed runtime** for the implemented systems abstraction;
- **Governed Runtime Intelligence (GRI)** for the broader conceptual framing;
- **reference factuality** for agreement/support relative to benchmark
  references;
- **evidence faithfulness** for support relative to evidence shown to the
  system;
- **coverage** for the fraction of cases in which an answer is executed;
- **defer** for evidence/confidence non-execution;
- **refuse** for policy-driven non-execution.

Do not use refusal as a generic synonym for every abstention.

## K. Equation and notation consistency

The architecture currently uses:
- q: query;
- P: policy decision;
- R: retrieval;
- S: evidence sufficiency;
- C: confidence;
- A: action;
- G: generation.

Retain this notation across the architecture and methodology.

The current confidence equation:

c = min(1, 0.65 s_e + 0.35 s_p)

must be described as an implementation heuristic, not a calibrated probability
or theoretically derived optimum.

## L. Reproducibility chain

The final manuscript or supplement should preserve the following integrity
chain:

- manifest SHA-256:
  62bd9c4b6bf8810a93a2065683f4d29a3f946246a45f2b1be98c6459e18b329c
- ordered item-ID SHA-256:
  ed9aac76d0529f736dcfe8265374d3919169f5102d7f6d6d76f1207f6e162c85
- clean raw SHA-256:
  61912c5fbbbefc57e3d17a6eee59addeabf7e4ae032c9e50d186896cc7d58479
- stress raw SHA-256:
  6722c132188e02db5c4bd0647475542e7f795b38fd6bbfe4f79e2d6524e63098
- clean NLI SHA-256:
  f22c3514b651d413b972125e4a577e6bb7733aa006deb2f3783852532b3b7f5c
- stress NLI SHA-256:
  ae678a2fdb381b0ebfaff06b3e81bb68cbdcb2d9d4bcf39fcb4f8e250bcec7c5

The corrected XSTest-combined file should also be frozen with a final checksum
before submission.

## M. Submission-readiness blockers

The manuscript should not yet be labelled final. The remaining high-priority
tasks are:

1. complete human validation of automated semantic metrics;
2. freeze and record the checksum of the corrected 26,000-row merged dataset;
3. expand and verify Related Work with full JAIR-style references;
4. generate final publication tables and figures from corrected artefacts;
5. draft Section 7 (Conclusion and Future Work);
6. perform a final claim-to-evidence audit;
7. convert the manuscript to the current JAIR Author Kit;
8. verify all figure/table/equation references and bibliography entries.

## N. Overall readiness judgement

The experimental core is now substantially stronger than the original
submission. The paper has a coherent systems contribution, reproducible
evaluation pipeline, transparent correction record, and statistically
defensible results.

The largest remaining scientific risk is not the L4 environment, the 48-hour
execution, or the stress design. It is the absence of completed human
validation for the automated NLI-based semantic metrics. Resolving that issue,
then strengthening the Related Work and final presentation, would materially
improve the manuscript's position for peer review.
