# Related Work and Architecture draft — JAIR v2.0 rebuild

## 2. Related Work

### 2.1 Retrieval-augmented generation and adaptive retrieval

Retrieval-augmented generation (RAG) combines parametric language-model
knowledge with external non-parametric evidence and has become a standard
approach for knowledge-intensive generation (Lewis et al., 2020). Its central
advantage is that model output can be conditioned on retrievable evidence
rather than relying exclusively on parameters learned during pre-training.
This improves knowledge updating and can provide provenance for generated
answers.

However, fixed retrieval alone does not determine whether retrieved evidence is
sufficient, contradictory, stale, or otherwise unsuitable for generation.
Subsequent work has therefore explored more adaptive forms of retrieval and
reflection. Self-RAG, for example, learns when to retrieve and uses
self-reflection signals to critique retrieved passages and generated responses
(Asai et al., 2024). These approaches show that retrieval itself can be made
conditional rather than indiscriminate.

OtiLLM is related to this line of work but addresses a different control level.
It does not claim a new retrieval model. Instead, retrieval is one signal in a
broader runtime decision process that can execute, defer, or refuse generation.
The present evaluation therefore asks not only whether evidence can be
retrieved, but whether the runtime should permit generation given the evidence
state.

### 2.2 Reasoning, acting, and agentic orchestration

ReAct integrates reasoning and acting by interleaving model-generated reasoning
with actions that query external environments or knowledge sources
(Yao et al., 2023). More broadly, agentic LLM systems increasingly combine
planning, tools, retrieval, memory, and iterative control.

This literature is relevant to OtiLLM because both approaches move beyond a
single prompt-to-response interaction. The distinction is that OtiLLM's primary
abstraction is governance rather than open-ended agency. Its publication
runtime exposes evidence sufficiency, policy decisions, confidence, memory
write state, and final action as explicit control variables. The bounded ReAct
baseline in this study is therefore used as an orchestration comparison, not as
a claim that the experiment reproduces unrestricted autonomous agents.

### 2.3 Guardrails, alignment, and policy control

LLM guardrails seek to constrain model behaviour at the input, output, or
system level. Recent surveys describe guardrails as a broad class of
safeguarding mechanisms for risks including harmful content, privacy,
hallucination, bias, and adversarial behaviour (Dong et al., 2024).
Constitutional AI similarly demonstrates that explicit principles can be used
to critique, revise, and train model behaviour toward safer outputs
(Bai et al., 2022).

These approaches establish the importance of policy constraints, but policy
compliance is only one dimension of runtime reliability. A request may be safe
yet unsupported by available evidence, or it may have strong evidence but be
disallowed by policy. OtiLLM therefore separates policy gating from evidence
sufficiency. The XSTest correction in the present study directly demonstrates
why this separation matters: missing evidence must not be treated as equivalent
to policy risk.

The paper does not introduce a new safety classifier. In the corrected XSTest
path, OtiLLM deliberately uses the same pinned semantic SAFE/UNSAFE
classification instruction as the dedicated Guardrail baseline. The empirical
claim is therefore about policy integration within the runtime, not classifier
novelty.

### 2.4 Selective prediction, abstention, and coverage

Selective prediction studies when a model should abstain rather than return a
potentially unreliable prediction. In selective question answering, the
objective is to maximise coverage subject to an acceptable error rate, making
abstention a first-class decision rather than a failure mode
(Kamath, Jia, and Liang, 2020).

This perspective is central to the present study. OtiLLM is intentionally
selective: evidence or confidence below threshold can produce deferral rather
than generation. Consequently, answer quality is reported jointly with
coverage. The selective stress analysis further compares baselines on the exact
subset of items OtiLLM answers, avoiding the misleading comparison between a
selective system's conditional quality and a non-selective system's
unconditional average.

OtiLLM extends the selective-prediction perspective by coupling abstention to
multiple runtime signals, including evidence sufficiency and policy state,
rather than treating abstention as a standalone confidence-calibration problem.

### 2.5 Faithfulness, factuality, and evidence-grounded generation

A recurring problem in LLM evaluation is the tendency to conflate factuality
with faithfulness. A response may be factually correct relative to a reference
while being unsupported by the evidence presented to the model. Conversely, a
strictly evidence-grounded response may be faithful but incomplete if the
retrieved context is insufficient.

The present work therefore separates reference factuality from evidence
faithfulness. This separation is especially important under contradictory,
incomplete, or stale evidence, where a model's parametric knowledge may produce
a correct answer that is not justified by the current evidence state. OtiLLM's
runtime objective is not simply to maximise reference agreement, but to control
whether generation is justified by the evidence available at inference time.

### 2.6 Memory and persistent LLM systems

Persistent memory is increasingly used to preserve user context, task state,
and prior outputs across interactions. While memory can improve continuity, it
also introduces governance questions concerning stale information,
contradictions, privacy, and unsafe persistence.

OtiLLM includes bounded memory-write gating, but the present paper does not
claim to have established longitudinal memory safety or long-term memory
benefits empirically. Governed Cognitive Memory and more advanced causal or
persistent memory mechanisms remain architectural directions rather than
validated contributions in this study. This boundary is maintained throughout
the evaluation.

### 2.7 Positioning of the present work

The closest neighbouring approaches address individual parts of the problem:
RAG provides external evidence; adaptive RAG decides when to retrieve;
ReAct coordinates reasoning and action; guardrails constrain unsafe behaviour;
and selective prediction formalises abstention. OtiLLM's contribution is to
place several of these signals inside a single runtime control loop and make
the final execution decision explicit.

The paper therefore positions OtiLLM as a systems abstraction for governed
inference. Its novelty claim is not that each underlying mechanism is new in
isolation, nor that the current implementation dominates specialised methods.
The contribution is the integration of evidence state, policy state,
confidence, selective execution, bounded memory persistence, and structured
trace capture into an auditable runtime decision process evaluated under a
common model backend.

## 3. OtiLLM Architecture and Governed Runtime Model

### 3.1 Design objective

OtiLLM is designed around a simple premise: generation should be an outcome of
runtime control rather than the default response to every input. The runtime
therefore represents and evaluates intermediate state before invoking the
generator.

For content tasks, the publication implementation follows the control path:

[
q \rightarrow P(q) \rightarrow R(q,E) \rightarrow S(E_q)
\rightarrow C(S,P) \rightarrow A \rightarrow G(q,E_q)
]

where (q) is the query, (P) is the policy decision, (R) is evidence
retrieval over candidate evidence (E), (S) is evidence sufficiency,
(C) is the runtime confidence signal, (A) is the selected action, and
(G) is generation when execution is permitted.

Generation is therefore conditional on policy, evidence, and confidence rather
than being unconditionally invoked.

### 3.2 Runtime state

The publication runtime records the following observable state:

- query;
- policy decision and policy score;
- retrieved source identifiers;
- retrieval scores;
- evidence-sufficiency score;
- confidence score;
- selected action;
- memory-write decision; and
- trace notes describing the control path.

This state is retained in a structured runtime trace. The trace is operational
rather than a hidden chain-of-thought representation: it records system events,
scores, and actions required for auditability without exposing private internal
reasoning.

### 3.3 Policy layer

The first runtime stage evaluates whether a request is permitted. For content
tasks, a failed policy check produces a blocking action before retrieval or
generation.

Policy-only tasks use a separate task-aware route. Following the XSTest
diagnostic correction, these tasks are not required to pass an external
evidence-sufficiency threshold. Instead, the runtime applies the static policy
check followed by a semantic SAFE/UNSAFE classifier. A permitted request can
then execute directly; a disallowed request is refused.

This separation prevents two semantically different causes of non-execution
from being conflated:

[
\text{policy risk} \neq \text{evidence insufficiency}.
]

### 3.4 Evidence retrieval and scoring

For content tasks, evidence is retrieved from the candidate evidence made
available by the common evaluation harness. Each evidence object contains
content, source information, metadata, timestamp, and a trust score. Retrieval
produces scored evidence objects that can incorporate semantic, keyword,
temporal, graph, provenance, and final retrieval scores.

The paper does not claim a new state-of-the-art retriever. The purpose of the
retrieval layer in the publication experiment is to provide the runtime with an
explicit evidence state on which governance decisions can operate.

### 3.5 Evidence sufficiency

After retrieval, the runtime computes an evidence-sufficiency score. This score
is used as a gate rather than merely as an explanatory statistic.

Let (s_e) denote evidence sufficiency and (	au_e) the configured evidence
threshold. The publication controller implements:

[
s_e < 	au_e \Rightarrow A = \text{defer/refine}.
]

When this condition holds, generation is not invoked. The runtime returns a
bounded response indicating that available evidence is insufficient.

This mechanism is the principal source of OtiLLM's selective behaviour in the
content experiments.

### 3.6 Confidence gating

The publication controller derives confidence from evidence sufficiency and
policy posture. In the current implementation,

[
c = \min\left(1, 0.65s_e + 0.35s_p\right),
]

where (s_e) is evidence sufficiency and (s_p) is the policy score.

If (c < 	au_c), where (	au_c) is the configured confidence threshold,
the runtime defers with a low-confidence action rather than invoking the
generator.

This equation is an explicit implementation rule in the evaluated controller;
it should not be interpreted as a learned or theoretically optimal confidence
model.

### 3.7 Action selection

The experimentally established content-task action set in the publication
runtime is bounded to:

- BLOCK;
- REFINE_OR_DEFER;
- DEFER_LOW_CONFIDENCE; and
- EXECUTE.

For policy-only tasks, REFUSE is additionally used after semantic policy
classification.

These actions are deliberately narrower than the broader OtiLLM architectural
vision. Clarification, escalation, forgetting, full retrieval reconsideration,
and learned action selection remain outside the validated publication path.

### 3.8 Generation

When policy, evidence, and confidence gates permit execution, the common
Qwen3-8B backend generates an answer using the selected evidence. The generator
instruction requires use of supplied evidence and asks the model to acknowledge
insufficient or conflicting evidence rather than invent support.

Because the same pinned model revision is used by OtiLLM and the model-based
baselines, experimental differences are attributable primarily to orchestration
and runtime-control choices rather than model scale or pre-training.

### 3.9 Bounded memory writing

After a successful content generation, OtiLLM may write the answer to memory
subject to confidence and policy constraints. The current study records the
memory-write decision but does not evaluate long-term memory quality across
sessions.

Accordingly, bounded memory writing is part of the executable runtime, whereas
longitudinal Governed Cognitive Memory remains outside the paper's established
empirical claims.

### 3.10 Structured runtime trace

Each OtiLLM request produces a structured trace containing policy outcome,
retrieval metadata, evidence sufficiency, confidence, action, and memory-write
state. This trace supports auditability and allows the evaluation harness to
measure common trace completeness across systems.

The trace should not be described as proof of correctness. It is an
instrumentation mechanism that records which runtime controls were applied and
which action resulted.

### 3.11 Relationship to the broader OtiLLM architecture

The repository contains a broader experimental runtime including uncertainty
estimation, Retrieval Reconsideration Dynamics, Cognitive Utility Optimisation,
Governed Memory, and an Explainable Runtime Reasoning Graph. These components
represent the larger architectural direction of OtiLLM.

However, the JAIR publication distinguishes architecture from validated
implementation. In the current experiment:

- evidence retrieval/scoring is evaluated;
- evidence sufficiency is evaluated;
- policy gating is evaluated;
- confidence gating is evaluated;
- execute/refuse/defer behaviour is evaluated;
- bounded memory-write gating is implemented but only lightly exercised; and
- structured operational tracing is evaluated.

By contrast, full failure-specific retrieval reconsideration, formal cognitive
utility optimisation, clarification/escalation/forget actions, longitudinal
memory governance, learned policies, and distinct Minimal/Balanced/Full
controller variants are not presented as empirically established.

### 3.12 Governed Runtime Intelligence as an abstraction

The broader abstraction underlying OtiLLM can be represented as a state-action
system:

[
x_t = (q_t, e_t, p_t, c_t, m_t, \pi_t),
]

where (q_t) is the current query, (e_t) is evidence state, (p_t) is
policy state, (c_t) is confidence, (m_t) is memory state, and (pi_t)
denotes provenance and trace state.

A governed runtime maps this state to an action:

[
a_t = \Gamma(x_t),
]

where (Gamma) is the runtime control policy and (a_t) may represent
execution, deferral, refusal, retrieval reconsideration, clarification, or
another governed action.

The present OtiLLM implementation instantiates a bounded subset of this action
space. The value of the abstraction is therefore not dependent on every action
being implemented in the current release. It provides a systems framework in
which evidence, safety, confidence, memory, and provenance can influence
execution through explicit state rather than remaining disconnected auxiliary
modules.

### 3.13 Architectural claim boundary

The paper deliberately avoids claiming that OtiLLM is the first system to use
retrieval, abstention, guardrails, memory, or traces. Each of these mechanisms
has substantial prior literature. Nor does it claim that the current runtime
solves trustworthy AI.

The architectural contribution is instead the governed-runtime formulation:
the final model invocation is treated as a controlled action conditioned on
multiple explicit runtime states. The empirical sections then test whether
this formulation produces measurable differences in coverage, faithfulness,
factuality, policy behaviour, and operational execution under a common
foundation model.
