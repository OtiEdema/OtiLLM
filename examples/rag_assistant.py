"""Slightly richer RAG-style example."""

from otillm import OtiLLM


def build_demo_runtime() -> OtiLLM:
    runtime = OtiLLM()
    runtime.add_evidence_batch(
        [
            {
                "content": "OtiLLM 3.0 uses an Evidence Fabric to combine semantic, keyword, temporal, graph, and provenance signals.",
                "source": "otillm_docs",
                "trust_score": 0.95,
            },
            {
                "content": "The Policy Engine blocks unsafe or non-compliant requests before execution.",
                "source": "otillm_policy_docs",
                "trust_score": 0.93,
            },
            {
                "content": "The Memory Engine writes only high-quality, policy-compliant, novel content.",
                "source": "otillm_memory_docs",
                "trust_score": 0.92,
            },
        ]
    )
    return runtime


if __name__ == "__main__":
    runtime = build_demo_runtime()
    question = "What makes OtiLLM different from normal RAG pipelines?"
    result = runtime.query(question)
    print(result.answer)
    print("\n--- TRACE ---\n")
    print(runtime.explain(result))
