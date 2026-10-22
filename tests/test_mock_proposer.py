
import pytest

from echomind.llm import MemoryProposal
from echomind.llm.policy import validate_proposal


class FakeProposer:
    """Simulate an LLM without network calls or API credentials."""

    def __init__(self, proposal):
        self.proposal = proposal

    def propose(self, text):
        return self.proposal


def test_valid_proposal_is_accepted():
    text = "I promised to finish the evaluation by Friday."
    proposer = FakeProposer(
        MemoryProposal(
            action="save",
            memory_type="commitment",
            content="finish the evaluation by Friday",
            evidence=text,
            confidence=0.95,
        )
    )

    proposal = proposer.propose(text)
    validate_proposal(text, proposal)


def test_unsupported_claim_cannot_be_saved():
    text = "The weather is nice today."
    proposer = FakeProposer(
        MemoryProposal(
            action="save",
            memory_type="commitment",
            content="Finish the project by Friday",
            evidence=text,
            confidence=0.99,
        )
    )

    with pytest.raises(ValueError):
        validate_proposal(text, proposer.propose(text))


def test_ambiguous_intention_cannot_be_saved_directly():
    text = "I should finish the evaluation."
    proposer = FakeProposer(
        MemoryProposal(
            action="save",
            memory_type="commitment",
            content=text,
            evidence=text,
            confidence=1.0,
        )
    )

    with pytest.raises(ValueError):
        validate_proposal(text, proposer.propose(text))


def test_proposer_cannot_turn_clear_commitment_into_confirmation():
    text = "I promised to finish the evaluation by Friday."
    proposer = FakeProposer(
        MemoryProposal(
            action="confirm",
            reason="The model thinks this is uncertain.",
        )
    )

    with pytest.raises(ValueError):
        validate_proposal(text, proposer.propose(text))


def test_ignoring_unsupported_text_is_allowed():
    text = "The weather is nice today."
    proposer = FakeProposer(
        MemoryProposal(
            action="ignore",
            reason="No supported memory detected.",
        )
    )

    validate_proposal(text, proposer.propose(text))
