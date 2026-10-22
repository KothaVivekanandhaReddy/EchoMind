
from pydoc import text

from echomind.llm.bedrock import (
    BedrockMemoryProposer,
    create_bedrock_client,
)
from echomind.llm.policy import validate_proposal
from echomind.extractor import assess_memory_text

def main():
    text = "I promised to finish the evaluation by Friday."

    client = create_bedrock_client(region_name="us-east-1")
    proposer = BedrockMemoryProposer(
        client=client,
        model_id="openai.gpt-oss-120b-1:0",
    )
    proposal = proposer.propose(text)

    print("Bedrock proposal received:")
    print(f"Action: {proposal.action}")
    print(f"Memory type: {proposal.memory_type}")
    print(f"Content: {proposal.content!r}")
    print(f"Evidence: {proposal.evidence!r}")
    print(f"Confidence: {proposal.confidence}")
    print(f"Reason: {proposal.reason!r}")

    assessment = assess_memory_text(text)
    extracted = assessment.get("memory")

    print("\nDeterministic extractor expects:")
    print("Action:", assessment["action"])

    if extracted:
        print("Memory type:", extracted.memory_type)
        print("Content:", repr(extracted.content))
        print("Evidence:", repr(extracted.evidence))
# Apply EchoMind's deterministic safety checks.
    validate_proposal(text, proposal)
    print("\nLive Bedrock adapter test passed.")


if __name__ == "__main__":
    main()
