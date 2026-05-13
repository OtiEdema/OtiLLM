# OtiLLM v2.4  
## A Governed Cognitive Runtime for Evidence-Native, Memory-Augmented and Explainable Frontier AI Systems

OtiLLM is a research-grade governed cognitive runtime framework designed to make Large Language Model systems more reliable, explainable, evidence-aware, and operationally trustworthy.

Unlike conventional Retrieval-Augmented Generation (RAG), agentic orchestration, or guardrail-based systems, OtiLLM treats inference as a governed runtime process rather than a simple prompt-to-response operation.

At runtime, OtiLLM continuously evaluates evidence sufficiency, contradiction density, uncertainty, governance risk, memory utility, retrieval quality, and explainability requirements before selecting an action.

OtiLLM can dynamically decide whether to answer, retrieve more evidence, reformulate retrieval, escalate uncertainty, refuse unsupported generation, update memory, or generate an explainable runtime trace.

---

## Why OtiLLM Exists

Modern frontier AI systems are increasingly powerful, but they remain vulnerable to hallucination, unsupported claims, weak retrieval grounding, poor uncertainty calibration, limited runtime explainability, unsafe memory persistence, fragile governance enforcement, and adversarial retrieval attacks.

The central idea behind OtiLLM is:

> Trustworthy AI requires governed cognition, not just larger models.

---

## Core Innovations

### Governed Cognitive Runtime
OtiLLM models inference as a continuously governed runtime process involving retrieval, governance, uncertainty, memory, utility optimisation, and explainability.

### Evidence Fabric
The Evidence Fabric evaluates retrieval quality, contradiction density, source reliability, freshness, and evidence sufficiency before reasoning proceeds.

### Retrieval Reconsideration Dynamics
Retrieval Reconsideration Dynamics enables OtiLLM to reformulate, expand, diversify, or refresh retrieval when evidence quality is insufficient.

### Cognitive Utility Optimisation
OtiLLM selects runtime actions according to expected cognitive utility under evidence and governance constraints.

### Governed Cognitive Memory
OtiLLM introduces confidence-aware and governance-constrained memory persistence to prevent unsafe, contradictory, or stale memory propagation.

### Explainable Runtime Reasoning Graph
The Explainable Runtime Reasoning Graph (ERRG) captures structured runtime provenance across evidence, governance, uncertainty, memory, and reasoning transitions.

---

## Installation

Install from source:

```bash
git clone https://github.com/OtiEdema/otillm.git
cd otillm
python -m pip install -e .
```

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

---

## Quick Start

```python
from otillm.runtime import GovernedRuntime

runtime = GovernedRuntime()
result = runtime.run("Who wrote Pride and Prejudice?")

print(result.answer)
print(result.action)
print(result.trace.to_dict())
```

---

## Benchmark Results

| Metric | Improvement |
|---|---|
| Truthfulness | +14.8% over Strong RAG |
| Faithfulness | +16.5% over Strong RAG |
| Unsupported claim reduction | 66.7% reduction |
| Adversarial retrieval robustness | 70.8% unsupported claim reduction |
| Refusal calibration | 91% accuracy |
| Trace completeness | +38% improvement |

---

## Running the JAIR Experiments

```bash
cd experiments/jair_v2

python prepare_jair_datasets.py
python run_jair_experiments.py
python run_jair_stress_tests.py
python statistical_validation.py
python plot_jair_results.py
```

Generated outputs:

```text
results/
├── jair_all_results.csv
├── jair_summary_results.csv
├── jair_stress_results.csv
├── jair_statistical_tests.csv
└── figures/
```

---

## Repository Structure

```text
otillm/
├── runtime/
├── governance/
├── retrieval/
├── evidence/
├── orchestration/
├── explainability/
├── memory/
├── multimodal/
├── benchmarks/
├── experiments/
├── notebooks/
├── docs/
├── tests/
└── examples/
```

---

## Citation

```bibtex
@article{edema2026otillm,
  title={OtiLLM v2.4: A Governed Cognitive Runtime for Evidence-Native, Memory-Augmented and Explainable Frontier AI Systems},
  author={Edema, Oti},
  journal={Submitted to the Journal of Artificial Intelligence Research},
  year={2026}
}
```

---

## Licence

MIT Licence.

---

## Author

Oti Edema  
GitHub: https://github.com/OtiEdema  
LinkedIn: https://www.linkedin.com/in/oti-e-34838485/
