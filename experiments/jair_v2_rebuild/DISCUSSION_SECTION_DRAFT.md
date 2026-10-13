# Discussion draft — JAIR v2.0 rebuild

## 6. Discussion

### 6.1 What the results show

The regenerated evaluation does not support the interpretation that OtiLLM is a universally more accurate answering system than conventional LLM, RAG, or agentic baselines. Instead, the results support a narrower and more methodologically defensible conclusion: OtiLLM changes the execution policy of an LLM system so that evidence quality, confidence, and policy state influence whether generation should proceed at all.

This distinction is visible in both the clean and stress evaluations. On clean content benchmarks, OtiLLM Balanced achieved lower token F1 and lower reference factuality than several baselines, while answering only 59.7% of content cases. The system therefore gives up answer coverage and some raw accuracy. At the same time, its clean evidence faithfulness exceeded that of Direct LLM and Guardrail LLM and was comparable to ReAct, indicating that the runtime is not simply refusing indiscriminately but is changing the relationship between available evidence and model output.

The stress evaluation makes the trade-off more explicit. When evidence became noisy, incomplete, contradictory, adversarial, or stale, OtiLLM reduced coverage rather than maintaining a fixed 100% answer rate. This behaviour differs fundamentally from Standard RAG, Strong RAG, and ReAct, which continued to produce answers on all stress cases. The selective statistical analysis shows that this abstention policy is associated with statistically significant gains in conditional evidence faithfulness against Strong RAG in four of five stress settings and against ReAct in three of five settings. The same analysis shows that OtiLLM also improves factuality over Standard RAG and ReAct in several conditions, although Strong RAG remains stronger in factuality in multiple settings.

The central empirical contribution is therefore not unconditional performance dominance. It is the demonstration that a governed runtime can expose and actively manage a reliability trade-off that conventional generation pipelines often leave implicit.

### 6.2 Governance–utility trade-off as a runtime property

The results suggest that answer coverage should be treated as a first-class runtime variable rather than an afterthought. Conventional benchmark reporting often rewards systems that answer every question, even when evidence quality is poor. In contrast, OtiLLM makes non-execution an explicit system action. This design changes how performance should be interpreted.

Under incomplete and stale evidence, OtiLLM coverage fell to approximately 26%. Under noisy evidence it was approximately 37%, and under adversarial evidence approximately 60%. These reductions are substantial, but they are not necessarily failures of the runtime. They represent a deliberate control response to evidence conditions that the runtime judged insufficiently reliable. The important question is therefore not only whether a system answers correctly, but whether it should have answered given the evidence state.

This is why unconditional accuracy and selective reliability must be reported together. A system that answers every query may obtain higher aggregate factuality while also exposing users to unsupported generations in low-quality evidence settings. Conversely, a highly conservative system may achieve strong conditional reliability by refusing too often. The useful operating point lies between these extremes. OtiLLM Balanced represents one such operating point, but the current evaluation does not establish it as globally optimal.

The broader implication is that governance should be evaluated as a runtime control problem with multiple objectives: answer utility, evidence support, abstention cost, policy compliance, and operational overhead. This framing is closer to how deployed AI systems are actually used than a single accuracy score.

### 6.3 Why faithfulness and factuality diverge

A key result is the divergence between evidence faithfulness and reference factuality. OtiLLM frequently improves faithfulness without becoming the most factual system. Strong RAG, in particular, remains substantially stronger on factuality in several stress conditions.

This distinction is conceptually important. Factuality asks whether an answer agrees with the benchmark reference. Faithfulness asks whether the answer is supported by the evidence that was actually available to the system. These properties can diverge. A model may produce a factually correct answer from prior parametric knowledge even when the supplied evidence is incomplete, contradictory, or stale. Such an answer may score well on factuality while being weakly grounded in the current evidence context. Conversely, a system that restricts itself to available evidence may be more faithful but less complete or less aligned with the reference answer.

For a governed runtime, faithfulness is particularly important because the runtime is intended to control what the system is justified in saying under a specific evidence state. The results therefore support keeping factuality and faithfulness as separate objectives rather than collapsing them into a single trust score.

At the same time, the factuality disadvantage relative to Strong RAG is a real limitation. Governance should not become a justification for unnecessary abstention or reduced answer quality. Future controller policies should therefore aim to preserve OtiLLM's evidence sensitivity while recovering more of the factual performance achieved by stronger retrieval pipelines.

### 6.4 Comparison with RAG and agentic baselines

The evaluation clarifies the relationship between OtiLLM and RAG. OtiLLM should not be described as a replacement for retrieval-augmented generation. In the current implementation, retrieval is one component within a wider runtime control loop. The empirical results reinforce this distinction.

Standard RAG provides strong evidence faithfulness in several conditions and is not significantly worse than OtiLLM on selective faithfulness after Holm correction. Strong RAG achieves superior factuality in multiple stress settings. These findings show that retrieval quality and evidence ranking remain critical. OtiLLM's contribution lies elsewhere: it adds runtime decisions about whether the retrieved evidence is sufficient, whether confidence is adequate, whether policy permits execution, and whether generation should be deferred.

The comparison with ReAct is similarly instructive. ReAct maintains full coverage and, in this implementation, uses a bounded planning step before final generation. OtiLLM exceeds ReAct in selective faithfulness under noisy, contradictory, and stale evidence, and in factuality under contradictory, incomplete, and adversarial evidence. However, these gains occur with substantially lower coverage. The result is therefore best understood as a difference in control policy rather than a general superiority of one reasoning paradigm over another.

### 6.5 Policy governance and the XSTest correction

The XSTest analysis exposed an implementation issue that was useful diagnostically. In the initial run, policy-only prompts were routed through the same evidence-sufficiency gate used for factual QA. Because XSTest prompts do not naturally provide external evidence, OtiLLM refused every safe prompt as well as every unsafe prompt. This produced perfect unsafe-answer avoidance but unusable safe-prompt coverage.

The correction separated policy-only governance from evidence sufficiency. The runtime now applies static policy checks and a semantic SAFE/UNSAFE classifier without requiring external retrieval evidence for policy-only tasks. After this change, OtiLLM achieved 90.0% policy correctness, with a 16.8% false-refusal rate on safe prompts and a 1.5% unsafe-answer rate on unsafe prompts.

Importantly, OtiLLM matched the dedicated Guardrail baseline exactly on these quantities. This outcome should not be presented as a policy-classification advantage because the corrected OtiLLM policy path intentionally uses the same pinned backend and the same semantic classification instruction as the Guardrail baseline. Instead, the result validates the architectural separation between policy governance and evidence governance within the runtime.

The episode also highlights a broader methodological lesson: governance mechanisms must be evaluated in a task-aware way. A refusal caused by missing evidence is not the same as a refusal caused by policy risk. Treating these as one action obscures failure modes and can make a system appear safer than it actually is.

### 6.6 Operational implications

OtiLLM's clean mean latency was 2.713 s, lower than Prompt Chain, Self-Checking LLM, ReAct, and Strong RAG, but slightly higher than Direct LLM. The runtime also invoked the model less frequently because abstained cases do not proceed to generation.

These operational results should be interpreted carefully. Reduced invocation count and lower average latency are partly consequences of selective non-execution. They do not imply that the OtiLLM generation path itself is always faster. A fair operational interpretation is therefore that runtime governance can reduce unnecessary model execution when evidence is inadequate, potentially lowering computational cost, but at the expense of lower answer coverage.

This trade-off may be attractive in applications where unsupported answers are more costly than deferred responses. Examples include regulated decision support, enterprise knowledge systems, safety-critical analytics, and environments where provenance requirements are explicit. The present experiments, however, do not directly evaluate end-user utility or domain-specific economic cost, so such deployment implications remain hypotheses rather than demonstrated outcomes.

### 6.7 Methodological implications

Several aspects of the evaluation were designed to reduce common sources of overclaiming. All enabled LLM-based systems use the same pinned Qwen3-8B backend. The benchmark manifest is frozen and checksummed. Stress perturbations are archived with the exact evidence shown to each system. Factuality and faithfulness are scored independently. Statistical comparisons use paired benchmark items, paired bootstrap confidence intervals, permutation tests, and Holm correction. XSTest is kept separate from content QA, and content macro averages weight the four benchmarks equally.

These choices matter because OtiLLM is a systems contribution rather than a foundation-model contribution. If different systems used different base models, retrieval corpora, or evaluation subsets, improvements could not be attributed to runtime control. The common-backend design therefore strengthens the interpretation that observed differences arise from orchestration and governance choices.

Nevertheless, automated NLI evaluation is not ground truth. The DeBERTa-based evaluator provides a reproducible independent signal, but its judgments may not fully capture semantic correctness, nuanced support, or answer usefulness. The planned human adjudication stage remains necessary to validate the automated findings.

### 6.8 Limitations

The current study has several limitations.

First, OtiLLM Balanced is the only runtime mode evaluated. Minimal and Full modes were intentionally excluded because the implementation does not yet provide sufficiently distinct controller policies to justify treating them as separate experimental systems.

Second, the policy engine remains relatively simple. The corrected XSTest path demonstrates task-aware policy separation, but the semantic classifier itself is shared with the Guardrail baseline. The present paper therefore evaluates policy integration, not a novel safety classifier.

Third, the contradiction and adversarial evidence perturbations are controlled synthetic stressors. They are useful for causal robustness testing but should not be interpreted as a complete model of real-world misinformation, poisoning, or source conflict.

Fourth, the retrieval setup provides systems with a common candidate evidence pool rather than reproducing a complete open-world retrieval stack. The evaluation therefore isolates runtime and evidence-handling behaviour more cleanly, but does not measure end-to-end search quality over the public web or a production vector database.

Fifth, TruthfulQA does not provide benchmark-native evidence in the same way as FEVER, HotpotQA, and Natural Questions. Results on this benchmark should therefore be interpreted as a closed-book or evidence-availability edge case rather than as a standard retrieval-grounding task.

Sixth, Strong RAG retains a clear factuality advantage in several conditions. This indicates that OtiLLM's evidence-aware abstention policy is not yet sufficient to maximise answer correctness. Better retrieval, reranking, contradiction handling, or adaptive recovery may improve this balance.

Seventh, the study evaluates short-run task performance rather than long-term memory behaviour, multi-session governance, causal memory effects, or persistent policy adaptation. These remain architectural capabilities rather than fully established empirical contributions in the current paper.

Finally, the corrected XSTest run followed an observed diagnostic failure. The correction was documented before revised results were generated, did not expose gold labels to the runtime, and was restricted to the policy-only execution path. Nevertheless, the paper should explicitly disclose this sequence so that readers can distinguish the original implementation defect from the corrected evaluation.

### 6.9 Implications for Governed Runtime Intelligence

The findings support Governed Runtime Intelligence as a systems abstraction rather than as a claim about a new underlying language model. The core idea is that an LLM application should maintain explicit runtime state about evidence, policy, confidence, provenance, and action eligibility, and use that state to decide whether and how generation proceeds.

OtiLLM provides one concrete implementation of this idea. The present experiments establish only a subset of the broader vision: evidence-aware retrieval, evidence-sufficiency gating, confidence-aware deferral, policy-aware execution, selective generation, limited memory writing, and structured traces. More ambitious capabilities such as learned control policies, longitudinal governed memory, formal causal state, full retrieval reconsideration, and optimisation across multiple action types remain future work.

This bounded interpretation is important. The empirical contribution is not that OtiLLM solves trustworthy AI. It is that explicit runtime governance can measurably alter how a common LLM behaves under degraded evidence and policy constraints, producing a different and often more controllable reliability profile than always-answer generation pipelines.

### 6.10 Discussion summary

The evaluation shows that OtiLLM is best understood as a governed execution layer rather than a higher-accuracy model. It trades coverage for conditional reliability, improves evidence faithfulness over several strong baselines under retrieval stress, integrates policy decisions without conflating them with evidence insufficiency, and records structured runtime state for auditability. At the same time, Strong RAG remains superior in factuality in several settings, Standard RAG remains competitive in faithfulness, and the current controller can be overly conservative.

These results therefore support a measured conclusion: governed runtime control is a promising systems mechanism for making LLM behaviour more evidence-aware, selective, and auditable, but its value depends on how well the controller balances abstention, factual accuracy, evidence support, and operational cost.
