# OtiLLM v2.0 implementation-status boundary

This document defines the claim boundary for the JAIR rebuild.

| Mechanism | Formal paper concept | Public v2.0 implementation | Publication status |
|---|---|---|---|
| Evidence retrieval/scoring | Yes | Yes | Can evaluate |
| Evidence sufficiency | Yes | Yes | Can evaluate |
| Policy gating | Yes | Yes | Can evaluate |
| Confidence gating | Yes | Yes | Can evaluate |
| Answer/execute | Yes | Yes | Can evaluate |
| Refuse/defer | Yes | Yes | Can evaluate |
| Memory write gating | Yes | Yes | Limited evaluation possible |
| Structured operational trace | Yes | Yes | Can evaluate under common schema |
| Retrieval reconsideration | Yes | Separate runtime path exists, but not integrated into the public wrapper used by the rebuild | Do not claim as fully evaluated yet |
| Failure-mode-specific RRD operators | Yes | Partial/prototype | Requires implementation + ablation |
| CUO utility equation | Yes | Prototype in otillm/runtime/utility.py | Not yet equivalent to the full formal action optimisation |
| Clarification action | Yes | Prototype in alternate runtime | Not yet validated in publication harness |
| Escalation action | Yes | Not demonstrated in current public wrapper | Architectural |
| Forget action | Yes | Not demonstrated | Architectural |
| Governed Cognitive Memory longitudinal behaviour | Yes | Gated writes exist | Architectural/partially implemented; not empirically established |
| Minimal/Balanced/Full policies | Yes | Mode field exists, but public wrapper does not yet change controller behaviour by mode | Disable separate variants until implemented |
| Learned action policy | Future direction | No | Future work |

The manuscript must not describe an architectural item as empirically demonstrated unless its publication-status entry is updated after executable tests are added.
