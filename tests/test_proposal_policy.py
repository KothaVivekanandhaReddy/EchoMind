
import pytest

from echomind.llm import MemoryProposal, RuleBasedProposer
from echomind.llm.policy import validate_proposal


def test_valid_rule_based_save_is_accepted():
    text = "I promised to finish the evaluation by Friday."
    proposal = RuleBasedProposer().propose(text)

    validate_proposal(text, proposal)


def test_unsupported_text_cannot_be_saved():
    text = "The weather is nice today."
    proposal = MemoryProposal(
        action="save",
        memory_type="commitment",
        content="Finish the project",
        evidence=text,
    )

    with pytest.raises(ValueError):
        validate_proposal(text, proposal)


def test_ambiguous_intention_cannot_be_saved_directly():
    text = "I should finish the evaluation."
    proposal = MemoryProposal(
        action="save",
        memory_type="commitment",
        content=text,
        evidence=text,
    )

    with pytest.raises(ValueError):
        validate_proposal(text, proposal)


def test_modified_evidence_is_rejected():
    text = "I promised to finish the evaluation by Friday."
    proposal = RuleBasedProposer().propose(text)

    altered = MemoryProposal(
        action="save",
        memory_type=proposal.memory_type,
        content=proposal.content,
        evidence="I promised to finish everything by Friday.",
        confidence=proposal.confidence,
    )

    with pytest.raises(ValueError):
        validate_proposal(text, altered)
