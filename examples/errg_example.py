from otillm.explainability import ERRGBuilder

builder = ERRGBuilder()
graph = builder.create_graph(
    query="What is the capital of Japan?",
    evidence=["Tokyo is the capital of Japan."],
    governance_events=["policy_ok"],
    uncertainty_score=0.08,
    action="answer",
)

print(graph.summary())
print(graph.to_dict())
