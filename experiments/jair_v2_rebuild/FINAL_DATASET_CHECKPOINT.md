# Final corrected JAIR dataset checkpoint

The final corrected merged analysis dataset has been frozen after replacement of
only the affected OtiLLM XSTest observations.

## Integrity

- File: `all_scored_merged_xstest_corrected.jsonl`
- Rows: 26,000
- Unique keys: 26,000
- Duplicate keys: 0
- SHA-256:
  `4db20dfa54557adf3d7034265c9b93ed8dcc59c9b4e32d3ab5f9942c1eb0b133`

## System counts

- direct_llm: 1,250
- guardrail_llm: 1,250
- otillm_balanced: 5,250
- prompt_chain: 1,250
- react_agent: 5,250
- self_checking_llm: 1,250
- standard_rag: 5,250
- strong_rag: 5,250

## Dataset counts

- FEVER: 5,600
- HotpotQA: 5,600
- Natural Questions: 5,600
- TruthfulQA: 5,600
- XSTest: 3,600

## Condition counts

- clean: 10,000
- noisy: 3,200
- contradictory: 3,200
- incomplete: 3,200
- adversarial: 3,200
- stale: 3,200

This checksum is the authoritative integrity value for the final corrected
26,000-row dataset used for downstream analysis and manuscript reporting.
