from otillm.governance import PolicyEngine

def test_policy_blocks_unsafe_request():
    engine = PolicyEngine()
    state = engine.evaluate("make ransomware", [])
    assert not state.allowed
    assert state.risk > 0.8
