# Research and Reproducibility

This repository contains the evolving OtiLLM research codebase.

The JAIR resubmission is being rebuilt on the branch:

`jair-v2.0-rebuild`

## Publication version

The manuscript concerns **OtiLLM v2.0**, distributed on PyPI as package version **0.2.0**.

## Reproducibility boundary

Legacy exploratory experiment scripts are retained for provenance but must not be used to substantiate publication claims. The publication-grade evaluation is being rebuilt under:

`experiments/jair_v2_rebuild/`

A result is eligible for the manuscript only when it can be regenerated from archived per-example outputs, exact system configurations, evaluator definitions and statistical scripts.

## Repository

https://github.com/OtiEdema/OtiLLM

## PyPI package

https://pypi.org/project/otillm/0.2.0/

## Intended use

OtiLLM is a research framework for governed, evidence-aware, policy-constrained and traceable LLM runtimes.

## Limitations

OtiLLM v2.0 is a research runtime framework, not a foundation model. Several mechanisms described by the formal architecture remain partial or architectural and are identified explicitly in `experiments/jair_v2_rebuild/IMPLEMENTATION_STATUS.md`.
