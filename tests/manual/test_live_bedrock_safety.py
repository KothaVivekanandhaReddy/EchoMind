
from echomind.llm.bedrock import (
    BedrockMemoryProposer,
    create_bedrock_client,
)
from echomind.llm.policy import validate_proposal


def main():
    proposer = BedrockMemoryProposer(
        client=create_bedrock_client(region_name="us-east-1"),
        model_id="openai.gpt-oss-120b-1:0",
    )

    cases = [
        {
            "text": "I should finish the evaluation.",
            "expected_action": "confirm",
        },
        {
            "text": "I didn't promise to finish the evaluation.",
            "expected_action": "ignore",
        },
    ]

    for case in cases:
        text = case["text"]
        expected = case["expected_action"]

        proposal = proposer.propose(text)

        print(f"\nInput: {text}")
        print(f"Expected action: {expected}")
        print(f"Proposed action: {proposal.action}")
        print(f"Memory type: {proposal.memory_type}")
        print(f"Content: {proposal.content!r}")
        print(f"Evidence: {proposal.evidence!r}")
        print(f"Reason: {proposal.reason!r}")

        from echomind.extractor import assess_memory_text

        assessment = assess_memory_text(text)
        print(f"Deterministic action: {assessment['action']}")

        try:
             validate_proposal(text, proposal)
        except ValueError as exc:
             print(f"Safety policy rejected proposal: {exc}")

        assert proposal.action == expected, (
            f"Expected {expected!r}, got {proposal.action!r} "
            f"for input: {text!r}"
        )

    print("\nLive Bedrock safety tests passed.")


if __name__ == "__main__":
    main()
