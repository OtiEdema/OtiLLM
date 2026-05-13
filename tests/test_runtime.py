from otillm.runtime import GovernedRuntime

def test_runtime_returns_result():
    runtime = GovernedRuntime()
    result = runtime.run("Who wrote Pride and Prejudice?")
    assert result.answer
    assert result.action in {"answer", "clarify", "refuse", "reconsider_retrieval"}
    assert result.trace.to_dict()["nodes"]
