# Benchmark provenance for the JAIR v2.0 rebuild

This file records the intended public sources and evaluation roles. It is not a substitute for archiving the exact local files and checksums used in the frozen run.

## TruthfulQA

- Upstream repository: https://github.com/sylinrl/TruthfulQA
- Canonical source file used by the builder: TruthfulQA.csv
- Benchmark size: 817 questions in the original benchmark.
- Evaluation role: open-ended answer correctness/truthfulness.
- Publication manifest uses a deterministic sample unless the final preregistration chooses the full set.

## FEVER

- Dataset family: FEVER fact verification.
- Evaluation role: SUPPORTS / REFUTES / NOT ENOUGH INFO claim verification.
- Important: claim metadata alone is not sufficient for evidence-grounded evaluation. The publication manifest must pair each claim with explicit evidence text resolved from the corresponding Wikipedia evidence source.
- The builder therefore requires both a claims file and an evidence lookup file and fails if only one is supplied.

## HotpotQA

- Upstream site: https://hotpotqa.github.io/
- Intended split: distractor validation.
- The public dataset contains 7,405 validation examples for the distractor configuration.
- Licence: CC BY-SA 4.0.
- Evaluation role: multi-hop question answering with explicit supporting facts.
- Gold evidence IDs are constructed from the provided title/sentence supporting-fact annotations.

## Natural Questions

- Upstream source: https://ai.google.com/research/NaturalQuestions/download
- Intended split: development.
- The original dataset reports 7,830 development examples.
- Licence: CC BY-SA 3.0.
- Evaluation role: real-user question answering over Wikipedia.
- Only examples with recoverable short-answer annotations are admitted to the open-answer publication manifest. Records without a recoverable reference are excluded rather than given an inferred answer.

## Frozen-run requirements

For every benchmark used in the paper, archive:

1. source URL and retrieval date;
2. exact file name/version;
3. SHA-256 checksum;
4. selection seed;
5. selected item IDs;
6. any evidence resolution or preprocessing script;
7. final JSONL manifest checksum.

The manuscript must report the frozen manifest counts actually used, not the preregistered defaults in configs/benchmarks.json.
