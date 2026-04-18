"""Quickstart example for OtiLLM 3.0."""

from otillm import OtiLLM


if __name__ == "__main__":
    model = OtiLLM()
    model.add_evidence(
        content="Retrieval-Augmented Generation combines retrieval with language generation to reduce hallucination.",
        source="rag_handbook",
        trust_score=0.9,
    )
    model.add_evidence(
        content="Strong enterprise AI systems need evidence grounding, policy controls, and auditability.",
        source="enterprise_ai_notes",
        trust_score=0.85,
    )
    model.add_evidence(
        content="Naive prompt-only systems often fail in regulated domains because provenance is weak.",
        source="governance_brief",
        trust_score=0.80,
    )

    response = model.query("Why is evidence grounding important in enterprise AI?")
    print("ANSWER:\n")
    print(response.answer)
    print("\nEXPLANATION:\n")
    print(model.explain(response))
