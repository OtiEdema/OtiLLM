# Results draft — JAIR v2.0 rebuild

## 5. Results

### 5.1 Evaluation overview

The regenerated evaluation comprises 10,000 clean observations and 16,000
retrieval-stress observations, for a total of 26,000 system-level outputs.
All headline comparisons use the same pinned Qwen3-8B backend. Clean content
results are macro-averaged with equal weight across TruthfulQA, FEVER,
HotpotQA, and Natural Questions. XSTest is reported separately as a policy
benchmark. Retrieval-stress analysis covers noisy, contradictory, incomplete,
adversarial, and stale evidence. Selective comparisons are paired on the exact
subset of benchmark items for which OtiLLM Balanced chose to answer.

### 5.2 Clean content performance

On clean content benchmarks, OtiLLM Balanced obtained a macro token F1 of
0.139, factuality of 0.230, evidence faithfulness of 0.414, an unsupported-claim
rate of 0.586, coverage of 0.597, and mean latency of 2.713 s. Relative to the
Direct LLM baseline, clean faithfulness was 29.4% higher and the unsupported-
claim rate was 13.8% lower. These gains were accompanied by materially lower
coverage: OtiLLM answered approximately 59.7% of clean content cases, whereas
most non-selective baselines answered all cases.

The clean results therefore do not support a universal accuracy advantage.
Direct LLM and ReAct achieved higher token F1, while Strong RAG achieved higher
reference factuality. The clean evaluation instead indicates a governance-
utility trade-off: OtiLLM sacrifices answer coverage and some raw answer
accuracy in exchange for stronger evidence alignment than several non-governed
baselines.

### 5.3 Selective robustness under retrieval stress

The effect of selective execution became clearer under degraded evidence.
OtiLLM reduced coverage in response to retrieval quality: coverage was 0.374
under noisy evidence, 0.730 under contradictory evidence, 0.263 under
incomplete evidence, 0.596 under adversarial evidence, and 0.261 under stale
evidence. By contrast, Standard RAG, Strong RAG, and ReAct answered all stress
cases. Consequently, stress comparisons were evaluated on matched items that
OtiLLM actually answered, with paired bootstrap confidence intervals and
paired permutation tests corrected using Holm's procedure.

#### 5.3.1 Evidence faithfulness

OtiLLM achieved statistically significant selective-faithfulness gains over
Strong RAG in four of five stress conditions. The mean paired improvement was
0.0628 under noisy evidence (95% CI [0.0394, 0.0862], Holm-adjusted
p=0.00150), 0.0531 under contradictory evidence (95% CI [0.0320, 0.0741],
p=0.00150), 0.1045 under incomplete evidence (95% CI [0.0750, 0.1348],
p=0.00150), and 0.1168 under stale evidence (95% CI [0.0863, 0.1493],
p=0.00150). The adversarial comparison against Strong RAG was not significant.

Against ReAct, OtiLLM showed significant selective-faithfulness improvements
under noisy evidence (Δ=0.0433, 95% CI [0.0133, 0.0726], Holm-adjusted
p=0.0468), contradictory evidence (Δ=0.0409, 95% CI [0.0184, 0.0621],
p=0.00220), and stale evidence (Δ=0.0589, 95% CI [0.0271, 0.0922],
p=0.00700). Improvements under incomplete and adversarial evidence did not
remain significant after multiple-comparison correction.

OtiLLM did not significantly exceed Standard RAG in selective faithfulness
after Holm correction. This is important: the results support stronger
faithfulness than Strong RAG and ReAct in several degraded-evidence settings,
but do not establish OtiLLM as uniformly more faithful than every RAG baseline.

#### 5.3.2 Reference factuality

Selective factuality followed a different pattern. OtiLLM significantly
outperformed Standard RAG under noisy evidence (Δ=0.1113, 95% CI
[0.0622, 0.1619], Holm-adjusted p=0.00150), contradictory evidence
(Δ=0.0579, 95% CI [0.0222, 0.0955], p=0.0100), incomplete evidence
(Δ=0.1379, 95% CI [0.0801, 0.1962], p=0.00150), and adversarial evidence
(Δ=0.0941, 95% CI [0.0598, 0.1297], p=0.00150). The stale-evidence
comparison was not significant.

Relative to ReAct, OtiLLM produced significantly higher factuality under
contradictory evidence (Δ=0.0902, 95% CI [0.0500, 0.1297],
Holm-adjusted p=0.00150), incomplete evidence (Δ=0.1436, 95% CI
[0.0871, 0.2001], p=0.00150), and adversarial evidence (Δ=0.0871,
95% CI [0.0516, 0.1230], p=0.00150). The noisy and stale comparisons were
not significant.

Strong RAG remained the strongest factuality baseline in several conditions.
OtiLLM was significantly lower than Strong RAG under noisy evidence
(Δ=-0.1871), contradictory evidence (Δ=-0.1555), incomplete evidence
(Δ=-0.1190), and stale evidence (Δ=-0.2653), all after Holm correction.
The adversarial difference did not remain significant. Thus, the evidence
does not support a claim that governed selective execution maximises factual
accuracy; rather, it changes the reliability profile by combining abstention
with stronger evidence alignment in selected conditions.

### 5.4 Policy-governance evaluation on XSTest

The initial XSTest run exposed an architectural confound: evidence-free policy
prompts were routed through OtiLLM's evidence-sufficiency gate, causing blanket
abstention. This behaviour was diagnosed before revised XSTest results were
generated. The runtime was then corrected so that policy-only tasks first
undergo static policy checking and semantic SAFE/UNSAFE classification, without
requiring external evidence. No XSTest gold label was exposed to the runtime,
and content QA and retrieval-stress execution remained unchanged.

After this correction, OtiLLM achieved 0.900 overall policy correctness
(405/450). On the 250 safe prompts, it answered 208 and falsely refused 42,
giving a safe-prompt accuracy of 0.832 and a false-refusal rate of 0.168. On
the 200 unsafe prompts, it correctly refused 197 and answered 3, yielding an
unsafe-prompt accuracy of 0.985 and an unsafe-answer rate of 0.015.

Compared with the non-policy-aware baselines, which each achieved 0.5556
overall policy correctness, OtiLLM's advantage was significant
(Holm-adjusted p=2.42×10^-24). OtiLLM matched the dedicated Guardrail baseline
exactly on overall policy correctness, false-refusal rate, and unsafe-answer
rate (McNemar p=1.0 for all three comparisons). Because the corrected OtiLLM
policy path intentionally uses the same pinned backend and classification
instruction as the Guardrail baseline, this result should be interpreted as
evidence that the runtime successfully integrates policy-aware execution, not
as evidence that its semantic classifier is superior to the dedicated
guardrail.

### 5.5 Operational trade-offs

OtiLLM's clean mean latency was 2.713 s. This was substantially lower than the
two-call Prompt Chain and Self-Checking baselines and lower than ReAct and
Strong RAG, but slightly higher than the Direct LLM baseline. The runtime also
reduced model invocation frequency by abstaining when evidence or confidence
thresholds were not met. Operational comparisons should therefore be read
jointly with coverage: lower invocation cost partly reflects deliberate
non-execution rather than uniformly faster generation.

### 5.6 Summary of empirical findings

The regenerated experiments support four conclusions. First, OtiLLM does not
dominate conventional baselines on raw clean-task accuracy. Second, under
retrieval degradation it exhibits a clear selective-execution behaviour,
reducing coverage as evidence quality deteriorates. Third, on the subset of
items it chooses to answer, OtiLLM achieves statistically significant
faithfulness gains over Strong RAG in four of five stress conditions and over
ReAct in three of five conditions, while also improving factuality over
Standard RAG and ReAct in several conditions. Fourth, after separating
policy-only control from evidence sufficiency, OtiLLM matches a dedicated
guardrail on XSTest policy behaviour while substantially outperforming
non-policy-aware systems.

Taken together, these results support OtiLLM as a governed runtime that exposes
and controls the trade-off between answer coverage, evidence support, factual
accuracy, and policy compliance. They do not support a claim of universal
superiority over RAG or other LLM orchestration strategies.
