
import pytest

from echomind.llm import MemoryProposal, RuleBasedProposer


def test_clear_commitment_produces_save_proposal():
    proposer = RuleBasedProposer()
    proposal = proposer.propose(
        "I promised to finish the evaluation by Friday."
    )

    assert proposal.action == "save"
    assert proposal.memory_type == "commitment"
    assert proposal.content
    assert proposal.evidence
    assert proposal.evidence in (
        "I promised to finish the evaluation by Friday.",
        proposal.evidence,
    )


def test_ambiguous_intention_requests_confirmation():
    proposer = RuleBasedProposer()
    proposal = proposer.propose("I should finish the evaluation.")

    assert proposal.action == "confirm"


def test_unsupported_text_is_ignored():
    proposer = RuleBasedProposer()
    proposal = proposer.propose("The weather is nice today.")

    assert proposal.action == "ignore"


def test_save_proposal_requires_evidence():
    proposal = MemoryProposal(
        action="save",
        memory_type="commitment",
        content="Finish the evaluation",
    )

    with pytest.raises(ValueError):
        proposal.validate()


def test_confidence_must_be_in_range():
    proposal = MemoryProposal(
        action="ignore",
        confidence=1.5,
    )

    with pytest.raises(ValueError):
        proposal.validate()
