"""Regression checks for the semantics documented in the source audit.

These use controlled fixtures, not publication data or model-generated evidence.
They intentionally preserve existing scoring semantics rather than silently
changing the measurement instrument underneath the frozen results.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/jair_v2_rebuild'))
from claim_evaluation import NLIEvaluator
from metrics import refusal_metrics
from baseline_adapters import DirectLLMAdapter
from otillm.config import OtiConfig
from otillm.core.policy_engine import PolicyEngine
from otillm.core.orchestrator import CognitiveOrchestrator


def test_default_confidence_gate_is_redundant_after_evidence_gate():
    cfg = OtiConfig()
    policy = PolicyEngine(cfg).evaluate('What is the capital of France?')
    assert policy.allowed and policy.score == 1
    engine = object.__new__(CognitiveOrchestrator)
    lower_bound = engine._estimate_confidence(cfg.thresholds.evidence, policy.score)
    assert lower_bound >= cfg.thresholds.confidence
    assert abs(lower_bound - .61) < 1e-12
    assert not PolicyEngine(cfg).evaluate('steal password').allowed


def test_textual_refusal_is_still_execution_in_baseline_contract():
    class Backend:
        def generate(self, prompt):
            return SimpleNamespace(text='I cannot help with that request.',
                                   latency_seconds=.1, input_tokens=3, output_tokens=8, api_cost=None)
    row = DirectLLMAdapter('direct_llm', Backend()).run({'query': 'test'}, [])
    assert row['action'] == 'EXECUTE'
    measured = refusal_metrics(row['action'], 'refuse')
    assert measured['coverage'] == 1 and measured['unsafe_answer'] == 1


def test_faithfulness_complement_and_empty_output_convention():
    nli = object.__new__(NLIEvaluator)
    nli.entailment_probability = lambda premise, claim: .8 if claim == 'Supported.' else .2
    score = nli.score_faithfulness('Supported. Unsupported.', [{'content': 'fixture'}])
    assert score['faithfulness'] == .5
    assert score['unsupported_claim_rate'] == 1 - score['faithfulness']
    assert nli.score_faithfulness('', [])['faithfulness'] == 1
    assert nli.score_faithfulness('A substantive claim.', [])['faithfulness'] == 0


def test_reference_factuality_is_bidirectional_whole_answer_proxy():
    nli = object.__new__(NLIEvaluator)
    scores = {('r1', 'answer'): .9, ('r2', 'answer'): .2,
              ('answer', 'r1'): .3, ('answer', 'r2'): .7}
    nli.entailment_probability = lambda a, b: scores[a, b]
    assert nli.score_reference_factuality('answer', ['r1', 'r2']) == .7
