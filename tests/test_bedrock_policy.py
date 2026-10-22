
import json

import pytest

from echomind.llm.bedrock import BedrockMemoryProposer
from echomind.llm.policy import validate_proposal


class FakeBedrockClient:
    def __init__(self, response):
        self.response = response

    def converse(self, **kwargs):
        return {
            "output": {
                "message": {
                    "content": [{"text": json.dumps(self.response)}]
                }
            }
        }


def make_proposer(action, memory_type, content, evidence, confidence=0.99):
    response = {
        "action": action,
        "memory_type": memory_type,
        "content": content,
        "evidence": evidence,
        "confidence": confidence,
        "reason": None,
    }
    return BedrockMemoryProposer(
        FakeBedrockClient(response),
        "test-model",
    )


def test_supported_commitment_passes_policy():
    text = "I promised to finish the evaluation by Friday."
    proposer = make_proposer(
        "save",
        "commitment",
        "finish the evaluation by Friday",
        text,
    )

    proposal = proposer.propose(text)
    validate_proposal(text, proposal)


def test_high_confidence_does_not_override_ambiguous_intention():
    text = "I should finish the evaluation."
    proposer = make_proposer(
        "save",
        "commitment",
        text,
        text,
        confidence=1.0,
    )

    proposal = proposer.propose(text)

    with pytest.raises(ValueError):
        validate_proposal(text, proposal)


def test_model_cannot_invent_evidence():
    text = "I promised to finish the evaluation by Friday."
    proposer = make_proposer(
        "save",
        "commitment",
        "finish all project tasks",
        "I promised to finish all project tasks by Friday.",
    )

    proposal = proposer.propose(text)

    with pytest.raises(ValueError):
        validate_proposal(text, proposal)


def test_model_cannot_turn_denial_into_commitment():
    text = "I did not promise to finish the evaluation."
    proposer = make_proposer(
        "save",
        "commitment",
        "finish the evaluation",
        text,
    )

    proposal = proposer.propose(text)

    with pytest.raises(ValueError):
        validate_proposal(text, proposal)
