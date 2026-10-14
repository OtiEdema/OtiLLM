# OtiLLM JAIR source audit — 14 October 2026

## Status and scope

**Not submission-ready.** This audit starts from publication branch commit
`42d6c4d3b4621d64151caad0399a08777611a232`. It compares the source, controller,
adapters and scoring code with the uploaded 27-page manuscript. It does not
verify or replace the 26,000 frozen observations, which are absent from this
Git snapshot. The original experimental run's exact code revision must still
be associated with its artefacts before treating today's code as the run record.

The uploaded PDF differs materially from the current source: the source already
has a structured abstract, 16 bibliography entries, dataset citations, proper
inline mathematics, URL commands and a LaTeX integrity table. The PDF has only
seven references and numerous conversion artefacts. Its filename or timestamp
is not sufficient evidence of which source generated it.

## Verified findings and consequences

| Finding | Code evidence | Consequence |
|---|---|---|
| Confidence gate is redundant at defaults | `otillm/config.py`, `core/policy_engine.py`, `core/orchestrator.py`: permitted static score is 1; evidence threshold .40; confidence .65*s_e+.35; confidence threshold .55 | Passing evidence gives confidence >= .61. No separate confidence-deferral effect can be claimed. This is a source-level deduction, not an experimental ablation result. |
| Action coverage is not substantive answer coverage | `metrics.refusal_metrics`, `baseline_adapters.BaseAdapter._pack` | Direct/RAG/ReAct adapters retain EXECUTE even when generated text refuses. Their 100% coverage is an adapter property. XSTest `unsafe_answer` measures execution on unsafe-labelled prompts, not harmful compliance. |
| Candidate-pool support differs from prompt faithfulness | `score_outputs.py`, `run_stress.py`, `baseline_adapters.evidence_block`, `core/generator.py` | Scoring joins the whole pool; generators can use top-five subsets, different rankings, or no evidence. Audit selected evidence and prompts before claiming prompt-level faithfulness. |
| Clean quality includes deferrals | `score_outputs.py`, `aggregate_results.py`, `macro_average.py` | Deferral text is scored and averaged. Clean headline comparisons are not answered-only quality. Report explicit denominators and separately assess substantive responses. |
| Unsupported rate is a complement | `claim_evaluation.NLIEvaluator.score_faithfulness` | Exactly 1 - faithfulness; not an independent corroborating metric. No-claim outputs score 1 by convention. |
| Reference factuality is whole-answer bidirectional NLI | `claim_evaluation.NLIEvaluator.score_reference_factuality` | It is min(max reference-to-answer entailment, max answer-to-reference entailment). Different references may maximise each direction. It is not claim-level verified correctness. |
| FEVER references are labels | `prepare_hf_manifest.py`, FEVER builder | SUPPORTS/REFUTES strings do not supply a natural-language factual reference for generic NLI. Evaluate label correctness separately and validate NLI conclusions. |
| Retrieval's semantic score is lexical Jaccard | `evidence/retrieval.py` | Do not imply embedding-based semantic retrieval. Score weights, top-k and source diversity are now documented. |
| Temporal retrieval depends on wall clock | `EvidenceRetriever._temporal_score` and adapter timestamp fallback | Seeds do not fully determine scores across dates. Preserve run timestamps and selected evidence; do not silently retrofit the frozen run. |
| Contradiction perturbation contains reference text | `perturbations.transform` | It is a constructed negation of the first gold reference. Disclose answer exposure and do not call it label-independent natural contradiction. |
| Stale perturbation only edits metadata | `perturbations.transform` | This tests timestamp sensitivity, not a changed factual world. TruthfulQA has no initial evidence; stale/incomplete do nothing to its pool. |
| Latency boundaries differ by execution path | `adapters.OtiLLMAdapter.run`, `baseline_adapters.BaseAdapter._pack` | Executed OtiLLM rows sum backend call latency; non-executed rows use orchestrator elapsed time. Neither is a consistent full-request latency measure. Retain descriptive values only. |
| Trace score counts true flags | `trace_schema.common_trace_completeness`, `adapters.py` | A false event can be correctly recorded; true flags do not prove trace correctness. Some flags are set unconditionally. Do not claim validated audit completeness. |
| Human validation is not completed | `HUMAN_EVALUATION_PROTOCOL.md`, manuscript | Export blank, blinded sheets and obtain real independent ratings. Do not generate adjudications or report agreement before labels exist. |
| Missing publication assets | Git tree | Frozen JSONL/CSV assets, tables and result figures must be supplied from the original archive. No fabricated replacement results were produced. |

## Changes in this review branch

- Corrected doubled `\\Delta` commands and removed empty acknowledgements.
- Retained already-fixed abstract, dataset citations and integrity table.
- Added exact code-backed retrieval, sufficiency, thresholds and evaluator definitions.
- Explained redundant confidence gating and limited claims accordingly.
- Distinguished controller actions, evaluation-pool support and output-level safety.
- Documented perturbation construction and remaining provenance limits.
- Added Adaptive-RAG and CRAG citations, verified against primary records:
  https://aclanthology.org/2024.naacl-long.389/ and
  https://arxiv.org/abs/2401.15884 . This is not a completed full-literature audit.
- Redrew Figure 1 with labelled paths and an explicit default-threshold note.
- Updated table/plot terminology without changing numeric input files or runtime behaviour.
- Added a fresh-directory build script that records input hashes, source revision,
  dirty-tree status and PDF hash; it requires Biber and real publication assets.
- Added four offline checks for measurement semantics. These are controlled
  fixtures, not evidence for publication performance.

## Validation performed

Four measurement-contract checks passed (called directly with Python because
pytest is not installed in the review environment). All 18 bibliography keys
are cited and all citation keys resolve in the source. Python compilation and
Git whitespace checks are included in the final verification. Figure 1 was
rendered and inspected separately.

A complete manuscript build and page-by-page approval are **not completed**:
the frozen publication asset directory is missing, and Biber is unavailable
in this review environment. The build script fails on missing inputs rather
than copying a stale PDF or substituting invented tables.

## Next actions, in order

1. Obtain the original `final_publication_assets` directory, frozen corrected
   manifest, scored/raw JSONL and run configuration/commit records. Check the
   published hashes before analysis; preserve originals read-only.
2. Audit response text for refusal/compliance, separately from controller actions.
   Review all XSTest outputs or a documented validation set; do not infer harm
   from the EXECUTE flag.
3. Audit exact generator evidence. Reconstruct only where archived traces and
   deterministic recorded inputs suffice. If exact exposure cannot be established,
   retain the narrower candidate-pool metric or run a new versioned campaign.
4. Report per-dataset results and task-appropriate FEVER accuracy. Separate clean
   executed/substantive outputs from abstention text; validate the NLI instrument
   using independent human labels before accepting revised factuality claims.
5. Predefine ablations and sensitivity analysis. Confidence-only removal at the
   current defaults is an expected null control, not an independent component gain.
   Lowering evidence thresholds requires outputs for newly executed items; these
   cannot be inferred from existing deferral messages. Compare against simple
   matched-coverage gates, and use held-out threshold selection where feasible.
6. Complete the literature and statistical-reference audit and related-work
   comparison, with claims grounded in the actual evaluated implementation.
7. Generate all tables/figures from verified inputs, rebuild with the supplied
   author kit, inspect the new PDF and complete the archival release/checklist.

No full model experiment, NLI rescoring or human validation was performed by
this patch. No acceptance or submission-readiness claim is made.
