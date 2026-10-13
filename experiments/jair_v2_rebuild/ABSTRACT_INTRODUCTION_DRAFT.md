# Abstract and Introduction draft — JAIR v2.0 rebuild

## Abstract

Large language model (LLM) applications increasingly combine retrieval,
reasoning, safety filters, memory, and tool orchestration, yet these mechanisms
are often evaluated independently and leave the final execution decision
implicit. This paper presents OtiLLM, a governed runtime for evidence-aware LLM
systems that makes evidence sufficiency, policy state, confidence, provenance,
and action eligibility explicit at inference time. Rather than modifying the
underlying foundation model, OtiLLM controls whether generation should proceed,
be deferred, or be refused.

We evaluate OtiLLM Balanced against seven comparison systems using a common
pinned Qwen3-8B backend across TruthfulQA, FEVER, HotpotQA, Natural Questions,
and XSTest. The clean evaluation comprises 10,000 observations, while a
retrieval-stress evaluation contributes 16,000 additional observations under
noisy, contradictory, incomplete, adversarial, and stale evidence. Independent
DeBERTa-based NLI scoring is used for factuality and evidence faithfulness, and
paired bootstrap confidence intervals, permutation tests, McNemar tests, and
Holm correction are used for inferential analysis.

On clean content benchmarks, OtiLLM achieves faithfulness of 0.414 at 0.597
coverage, corresponding to 29.4% higher faithfulness and a 13.8% lower
unsupported-claim rate than Direct LLM, although it does not maximise raw
accuracy. Under degraded retrieval, OtiLLM significantly improves selective
faithfulness over Strong RAG in four of five stress conditions and over ReAct
in three of five conditions. It also improves selective factuality over
Standard RAG in four conditions and ReAct in three, while Strong RAG remains
stronger in factuality in several settings. On XSTest, OtiLLM attains 90.0%
policy correctness, with a 16.8% false-refusal rate and a 1.5% unsafe-answer
rate, matching a dedicated guardrail baseline.

These results support OtiLLM as a governed execution layer that makes the
trade-off between coverage, evidence support, factuality, and policy compliance
explicit. They do not support universal superiority over RAG or agentic
baselines; instead, they show that runtime governance can produce a more
selective and controllable reliability profile under degraded evidence and
policy constraints.

## 1. Introduction

### 1.1 Motivation

Modern LLM applications increasingly rely on more than a single prompt and a
single model call. Retrieval-augmented generation introduces external
knowledge; self-checking pipelines attempt to revise errors; agentic systems
introduce planning and tool use; guardrails apply safety or policy constraints;
and memory systems preserve information across interactions. These mechanisms
improve capability, but they also make system behaviour harder to reason about.
In many deployments, the critical decision is no longer only what answer a
model should generate, but whether it should generate at all given the current
evidence, confidence, policy state, provenance, and operational constraints.

Most existing LLM evaluation still treats these concerns separately. Retrieval
quality may be measured independently of refusal behaviour, safety independently
of evidence quality, and answer accuracy independently of whether the available
evidence justified answering. This separation can obscure important failure
modes. A system may remain factually correct because the model recalls an
answer from parametric knowledge even when the supplied evidence is stale or
contradictory. Conversely, a highly conservative system may appear reliable by
refusing too often. Neither behaviour is captured adequately by a single
accuracy score.

This paper investigates a different systems perspective: LLM behaviour can be
governed at runtime by making key decision variables explicit and using them to
control execution. We refer to this broader design perspective as Governed
Runtime Intelligence and present OtiLLM as a concrete implementation of that
idea.

### 1.2 OtiLLM as a governed runtime

OtiLLM is designed as a runtime layer around a common LLM backend rather than
as a replacement foundation model. The runtime receives a query, evaluates
policy constraints, retrieves or receives evidence, estimates evidence
sufficiency, derives a confidence signal, and decides whether to execute,
defer, or refuse. The system also records structured traces and supports
bounded memory-write decisions.

The central design principle is that governance variables should be represented
as first-class runtime state. Evidence quality, confidence, provenance, policy
status, and action eligibility are therefore not treated merely as explanatory
metadata after generation. They influence whether generation occurs.

This framing distinguishes OtiLLM from conventional RAG. Retrieval is one
component of the runtime, not the complete control strategy. It also
distinguishes OtiLLM from a simple guardrail, because policy is only one of the
signals that can affect execution. The runtime is intended to coordinate
multiple forms of control within a single inference path.

### 1.3 Research problem

The paper addresses the following research problem:

How does an explicit governed runtime affect the reliability profile of a
common LLM when evidence quality and policy constraints vary?

This question is deliberately narrower than asking whether OtiLLM is the most
accurate answering system. The study instead examines whether runtime
governance changes the trade-off among answer coverage, evidence faithfulness,
reference factuality, unsupported claims, policy compliance, and operational
cost.

Three empirical questions guide the evaluation:

**RQ1.** Does OtiLLM alter clean-task reliability relative to conventional LLM,
RAG, self-checking, guardrail, and bounded agentic baselines when the underlying
generator is held constant?

**RQ2.** Under degraded retrieval evidence, does selective execution improve
conditional evidence faithfulness or factuality on the items OtiLLM chooses to
answer?

**RQ3.** Can policy-only execution be separated from evidence-sufficiency
gating so that the runtime handles safe and unsafe requests without conflating
missing evidence with policy risk?

### 1.4 Contributions

This paper makes the following contributions.

First, it introduces a runtime-control abstraction in which evidence
sufficiency, policy state, confidence, provenance, and action eligibility are
explicitly represented and used to govern LLM execution.

Second, it provides OtiLLM as an executable implementation of this abstraction,
including evidence retrieval and scoring, evidence-sufficiency gating,
confidence-aware deferral, policy-aware execution, selective generation,
bounded memory writing, and structured tracing.

Third, it develops a reproducible evaluation design that holds the foundation
model fixed across systems and evaluates governance behaviour across clean
content tasks, retrieval-stress conditions, and policy prompts. The final
campaign contains 26,000 system-level observations, all traceable to frozen
per-example outputs and pinned model revisions.

Fourth, it introduces a matched-subset selective evaluation protocol in which
baseline systems are compared on the exact items OtiLLM chooses to answer, with
coverage reported jointly with conditional factuality and faithfulness. This
avoids conflating abstention with answer quality.

Fifth, it provides empirical evidence that runtime governance changes the
reliability profile of a common LLM. OtiLLM does not dominate on raw clean
accuracy, but under degraded retrieval it achieves statistically significant
selective-faithfulness gains over Strong RAG in four of five stress conditions
and over ReAct in three of five conditions. It also improves selective
factuality over Standard RAG and ReAct in several conditions, while Strong RAG
retains an advantage in factuality in multiple settings.

Sixth, it demonstrates policy-aware runtime integration on XSTest. After
separating policy-only execution from evidence sufficiency, OtiLLM reaches
90.0% policy correctness and matches a dedicated guardrail baseline on overall
correctness, false-refusal rate, and unsafe-answer rate.

The contribution is therefore not a claim that OtiLLM universally outperforms
RAG, agents, or guardrails. It is a systems contribution showing that explicit
runtime governance can make the interaction among evidence quality, abstention,
policy, and generation measurable and controllable.

### 1.5 Scope and claim boundary

The present work evaluates OtiLLM Balanced only. Minimal and Full modes are not
included because they are not yet sufficiently distinct in executable policy
behaviour. Similarly, the study does not claim to establish learned governance,
longitudinal memory safety, causal memory effects, or unrestricted agentic tool
use.

The empirical claims are restricted to the mechanisms directly exercised by
the evaluation: evidence-aware retrieval, sufficiency gating, confidence-aware
deferral, policy-aware execution, selective generation, limited memory writing,
and trace capture. Controlled contradictory and adversarial perturbations are
used as synthetic stressors and are not presented as complete models of
real-world misinformation or poisoning.

This bounded claim scope is central to the paper. The goal is not to argue that
OtiLLM solves trustworthy AI, but to determine whether runtime governance
provides a useful systems mechanism for controlling LLM behaviour under
uncertain evidence and policy constraints.

### 1.6 Paper organisation

The remainder of the paper is organised as follows. Section 2 reviews related
work on retrieval-augmented generation, self-verification, guardrails, agentic
orchestration, selective prediction, and runtime governance. Section 3 presents
the OtiLLM architecture and governed runtime abstraction. Section 4 describes
the reproducible experimental methodology. Section 5 reports the regenerated
evaluation results. Section 6 discusses the governance–utility trade-off,
limitations, and implications. The final section summarises the contribution
and outlines future work.
