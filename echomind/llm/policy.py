
from echomind.extractor import assess_memory_text
from echomind.llm.interface import MemoryProposal


def validate_proposal(text: str, proposal: MemoryProposal) -> None:
    """Reject proposals that conflict with deterministic extraction policy."""
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    proposal.validate()

    assessment = assess_memory_text(text)

    if proposal.action == "save":
        if assessment["action"] != "save":
            raise ValueError(
                "Cannot save: deterministic policy does not permit it."
            )

        extracted = assessment["memory"]

        if proposal.memory_type != extracted.memory_type:
            raise ValueError("Proposed memory type conflicts with policy.")

        if proposal.evidence != extracted.evidence:
            raise ValueError("Proposed evidence does not match extracted evidence.")

        if proposal.content != extracted.content:
            raise ValueError("Proposed content conflicts with extracted content.")

    elif proposal.action == "confirm":
        if assessment["action"] != "confirm":
            raise ValueError(
                "Confirmation is not permitted for this input."
            )

    elif proposal.action == "ignore":
        # Ignoring a candidate is always safe.
        return
