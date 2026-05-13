from otillm.explainability import ERRGBuilder

def test_errg_graph():
    graph = ERRGBuilder().create_graph("q", ["e"], ["policy_ok"], 0.1)
    assert len(graph.nodes) == 5
    assert len(graph.edges) == 4
