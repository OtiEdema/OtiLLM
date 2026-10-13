# Methodology draft — JAIR v2.0 rebuild

## 4. Methodology

### 4.1 Research design

This study evaluates OtiLLM as a governed runtime layer rather than as a new
foundation model. The experimental design therefore holds the underlying
language model fixed and varies the orchestration and control strategy. The
primary objective is to determine whether explicit runtime control over
evidence sufficiency, policy state, confidence, abstention, and trace
generation changes system behaviour under clean and degraded evidence
conditions.

The evaluation is organised around four principles. First, all reported
performance values must be derivable from per-example raw outputs. Second,
clean and stress conditions must differ through explicit, deterministic
evidence transformations. Third, correctness, factuality, evidence
faithfulness, unsupported-claim rate, refusal behaviour, coverage, latency,
and model-use cost are reported separately rather than collapsed into a
single trust score. Fourth, statistical comparisons are paired on benchmark
items so that differences reflect system behaviour on the same underlying
examples.

OtiLLM Balanced is the only OtiLLM configuration included in the primary
comparison. Minimal and Full modes are excluded because their controller
policies are not yet sufficiently distinct in executable code to justify
treating them as independent experimental systems.

### 4.2 Experimental systems

Eight systems are evaluated in the clean benchmark:

1. Direct LLM;
2. Prompt Chain;
3. Standard RAG;
4. Strong RAG;
5. Self-Checking LLM;
6. Guardrail LLM;
7. a bounded ReAct-style agent; and
8. OtiLLM Balanced.

For retrieval-stress testing, only the four systems that consume the common
evidence context are evaluated: Standard RAG, Strong RAG, ReAct, and OtiLLM
Balanced.

All enabled LLM-based systems use the same pinned generator backend:
Qwen/Qwen3-8B, revision
`a0809d1efaf104a46bbc2acaecd69617e9696312`. Generation is performed in
non-thinking mode using deterministic greedy decoding, temperature 0.0, and a
maximum generation length of 256 tokens. Holding the generator constant is
essential because the paper evaluates the effect of runtime orchestration and
governance rather than differences in foundation-model capability.

The comparison systems are implemented through a common evaluation harness.
Direct LLM performs a single unconstrained model call. Prompt Chain produces a
draft and a second-pass revision. Standard RAG conditions generation on the
common candidate evidence supplied by the harness. Strong RAG additionally
orders candidate evidence by retrieval or trust score before generation.
Self-Checking LLM generates a draft followed by an explicit correction pass.
Guardrail LLM performs a separate SAFE/UNSAFE classification before answer
generation. ReAct uses a bounded planning step followed by answer generation;
it is not described as a full open-world iterative retrieval agent because the
current implementation does not perform unrestricted external tool use or an
independent second search.

### 4.3 OtiLLM execution path

OtiLLM receives the same underlying model backend as the baselines but routes
queries through an explicit runtime controller. For content tasks, the
controller applies policy evaluation, retrieves candidate evidence, estimates
evidence sufficiency, derives a confidence signal, and either executes
generation or defers when the evidence or confidence threshold is not met.
Successful executions may also trigger a bounded memory-write decision and
produce a structured runtime trace.

The experimentally established components in this study are therefore:
evidence retrieval and scoring, evidence-sufficiency gating, policy gating,
confidence-aware deferral, selective execution, limited memory writing, and
structured trace generation. More ambitious architectural elements, including
fully learned control policies, longitudinal governed memory, causal memory
graphs, full retrieval reconsideration, and formally distinct Minimal and Full
runtime modes, are not treated as empirically established contributions in the
present evaluation.

### 4.4 Benchmark construction and frozen manifest

The benchmark manifest was constructed deterministically from canonical public
datasets using hash-based sampling with seed 42. The final frozen manifest
contains 1,250 records:

- TruthfulQA: 200;
- FEVER: 200;
- HotpotQA: 200;
- Natural Questions: 200; and
- XSTest: 450, comprising 250 safe and 200 unsafe contrast prompts.

The corrected frozen manifest has SHA-256
`62bd9c4b6bf8810a93a2065683f4d29a3f946246a45f2b1be98c6459e18b329c`.
The ordered item-ID checksum is
`ed9aac76d0529f736dcfe8265374d3919169f5102d7f6d6d76f1207f6e162c85`.

TruthfulQA is treated as a closed-book or evidence-availability edge case
because it does not provide benchmark-native evidence in the same form as
FEVER, HotpotQA, and Natural Questions. XSTest is evaluated separately as a
policy benchmark rather than being included in content macro averages.

### 4.5 Clean evaluation

The clean evaluation executes all eight systems on all 1,250 frozen benchmark
items, producing 10,000 observations. Each system therefore contributes 1,250
clean observations. The merged clean result contains exactly 10,000 unique
system-item-condition keys with no duplicates.

The clean merged result is frozen with SHA-256
`61912c5fbbbefc57e3d17a6eee59addeabf7e4ae032c9e50d186896cc7d58479`.

Content macro averages are computed with equal weight across TruthfulQA,
FEVER, HotpotQA, and Natural Questions. XSTest is excluded from these content
macro averages and is analysed separately using policy metrics.

### 4.6 Retrieval-stress evaluation

Robustness is evaluated under five degraded-evidence conditions:

- noisy;
- contradictory;
- incomplete;
- adversarial; and
- stale.

The clean condition is taken from the clean evaluation rather than duplicated
inside the stress run. Stress testing is restricted to the 800 content items
from TruthfulQA, FEVER, HotpotQA, and Natural Questions and to the four
retrieval-consuming systems. This yields 16,000 stress observations:
800 items × 5 perturbation conditions × 4 systems.

Each transformed evidence set is archived in the corresponding raw result row,
so subsequent faithfulness scoring is performed against the exact evidence
that the system actually received.

Contradictory and adversarial conditions are controlled synthetic stressors.
They are used to test sensitivity to structured evidence corruption and are
not presented as complete models of real-world misinformation, retrieval
poisoning, or malicious knowledge-base compromise.

The merged stress result contains 16,000 rows, 16,000 unique keys, and zero
duplicates. Its SHA-256 is
`6722c132188e02db5c4bd0647475542e7f795b38fd6bbfe4f79e2d6524e63098`.

### 4.7 Cloud execution environment and long-running experimental procedure

The final publication experiments were executed in a Google Colab cloud
environment backed by an NVIDIA L4 GPU. The complete experimental campaign was
performed over approximately 48 hours of cumulative execution and validation
rather than as a single uninterrupted notebook run.

The long-running workflow was divided into deterministic stages so that
transient notebook disconnections did not invalidate completed work. Raw
outputs and intermediate artefacts were checkpointed to persistent Google
Drive storage after each stage. The workflow comprised:

1. frozen-manifest validation;
2. clean-generation shards;
3. clean shard merge and integrity verification;
4. retrieval-stress generation shards;
5. stress shard merge and integrity verification;
6. independent NLI scoring of clean outputs;
7. independent NLI scoring of stress outputs;
8. aggregate metric calculation;
9. selective paired statistical validation;
10. XSTest policy analysis; and
11. generation of publication tables and figures.

Generation and scoring were intentionally separated. This prevents the model
under evaluation from serving as its own semantic judge and allows generated
outputs to be frozen before downstream evaluation.

Deterministic sharding was used to make long runs resumable. A shard was only
admitted to downstream analysis after row counts, expected system/dataset
balance, unique keys, and duplicate counts had been checked. Merged artefacts
were subsequently frozen by checksum.

The use of an L4 GPU is reported solely as part of experimental
reproducibility. No claim of algorithmic superiority is inferred from the
hardware configuration or wall-clock duration.

### 4.8 Independent factuality and faithfulness evaluation

Generated outputs are evaluated after generation using the independent NLI
model MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli, revision
`6f5cf0a2b59cabb106aca4c287eed12e357e90eb`, with an entailment threshold
of 0.5.

The evaluator is used to derive two distinct semantic outcomes:

- reference factuality: whether the generated claim is supported by the
  benchmark reference; and
- evidence faithfulness: whether the generated claim is supported by the exact
  evidence exposed to the system.

Unsupported-claim rate is reported separately rather than inferred from
factuality alone.

The clean NLI-scored file contains 10,000 unique observations and has SHA-256
`f22c3514b651d413b972125e4a577e6bb7733aa006deb2f3783852532b3b7f5c`.
The stress NLI-scored file contains 16,000 unique observations and has SHA-256
`ae678a2fdb381b0ebfaff06b3e81bb68cbdcb2d9d4bcf39fcb4f8e250bcec7c5`.

The NLI evaluator is treated as an automated measurement instrument, not as
ground truth. A stratified double-adjudicated human validation stage is
therefore retained as part of the final evaluation protocol.

### 4.9 Coverage and selective evaluation

OtiLLM is a selective system: it can execute, defer, or refuse. Consequently,
conditional answer quality cannot be interpreted without reporting answer
coverage.

For each stress condition, OtiLLM coverage is first measured over the full
condition. Selective factuality and selective faithfulness are then computed
only over items OtiLLM chose to answer. Baseline systems are compared on the
exact same item IDs, avoiding the unfair comparison that would arise if
OtiLLM's answered subset were compared with baseline averages over all items.

This matched-subset design is particularly important because Standard RAG,
Strong RAG, and ReAct maintain full coverage in the stress experiments,
whereas OtiLLM intentionally abstains under insufficient evidence.

### 4.10 Statistical analysis

The benchmark item is the primary paired statistical unit.

For continuous per-item metrics such as factuality and faithfulness, system
differences are evaluated using paired bootstrap confidence intervals with
5,000 resamples and paired permutation tests with 10,000 permutations.
Holm's procedure is applied to control the family-wise error rate across the
planned multiple comparisons.

For XSTest's binary policy outcomes, paired McNemar exact tests are used, with
Holm correction applied within metric families.

The main policy outcomes are:

- overall refusal correctness;
- false-refusal rate on safe prompts; and
- unsafe-answer rate on unsafe prompts.

Effect direction, confidence intervals, adjusted p-values, matched sample size,
and OtiLLM coverage are reported together. Statistical significance is not used
to mask practically unfavourable trade-offs such as low coverage.

### 4.11 XSTest policy-path correction and disclosure

The first frozen XSTest run revealed a structural implementation confound:
policy-only prompts were incorrectly routed through the evidence-sufficiency
gate used for content QA. Because XSTest does not naturally supply external
evidence, this caused blanket abstention: all 250 safe prompts and all 200
unsafe prompts were withheld.

The issue was diagnosed before corrected XSTest results were generated. The
runtime was then changed so that policy-only tasks are handled by a separate
execution path. The correction:

1. passes the task type as runtime context;
2. applies the static runtime policy first;
3. applies a semantic SAFE/UNSAFE classifier using the same pinned model and
   the same classification instruction as the Guardrail baseline;
4. permits safe policy-only prompts to execute without external evidence;
5. refuses unsafe prompts; and
6. leaves all content QA and retrieval-stress execution unchanged.

No XSTest gold policy label is exposed to the runtime. Only the affected 450
OtiLLM XSTest observations were regenerated. All clean content outputs,
retrieval-stress outputs, and their corresponding NLI scores remained
unchanged.

The original diagnostic failure is retained in the experimental record rather
than silently discarded. The corrected XSTest result is therefore interpreted
as validation of task-aware separation between policy governance and evidence
governance, not as post-hoc optimisation against benchmark labels.

### 4.12 Reproducibility and artefact integrity

The evaluation pipeline records both configuration identity and result
integrity. The principal frozen artefacts are:

| Artefact | Size / count | Integrity value |
|---|---:|---|
| Frozen benchmark manifest | 1,250 items | SHA-256 62bd9c4b6bf8810a93a2065683f4d29a3f946246a45f2b1be98c6459e18b329c |
| Clean raw results | 10,000 rows | SHA-256 61912c5fbbbefc57e3d17a6eee59addeabf7e4ae032c9e50d186896cc7d58479 |
| Stress raw results | 16,000 rows | SHA-256 6722c132188e02db5c4bd0647475542e7f795b38fd6bbfe4f79e2d6524e63098 |
| Clean NLI-scored results | 10,000 rows | SHA-256 f22c3514b651d413b972125e4a577e6bb7733aa006deb2f3783852532b3b7f5c |
| Stress NLI-scored results | 16,000 rows | SHA-256 ae678a2fdb381b0ebfaff06b3e81bb68cbdcb2d9d4bcf39fcb4f8e250bcec7c5 |

Together, these controls make it possible to distinguish planned evaluation
choices from later analysis, verify that all reported aggregate values are
traceable to per-example outputs, and reproduce the primary experimental
pipeline from frozen inputs and pinned model revisions.

### 4.13 Threats to validity

Several threats to validity remain. The common evidence pool isolates runtime
behaviour but does not measure unrestricted open-world retrieval quality.
Controlled synthetic contradictory and adversarial perturbations may not
capture the complexity of real-world source conflict. Automated NLI scoring may
misjudge nuanced semantic support. TruthfulQA does not expose benchmark-native
evidence in the same way as the other content datasets. The shared policy
classifier used by OtiLLM and the Guardrail baseline means XSTest evaluates
policy integration rather than classifier novelty. Finally, the current study
does not establish the longitudinal behaviour of governed memory, causal
reasoning, or learned adaptive policies.

These limitations bound the paper's claims. The methodology is designed to
support conclusions about runtime governance, selective execution, and
evidence-aware control under the tested conditions, not universal superiority
or complete trustworthy-AI coverage.
