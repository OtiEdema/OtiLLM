from otillm.runtime import GovernedRuntime

runtime = GovernedRuntime()
result = runtime.run("Who wrote Pride and Prejudice?")

print("Answer:", result.answer)
print("Action:", result.action)
print("Confidence:", result.confidence)
print("Trace:", result.trace.to_dict())
