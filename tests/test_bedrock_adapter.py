
import json

import pytest

from echomind.llm.bedrock import BedrockMemoryProposer


class FakeBedrockClient:
    def __init__(self, response_text):
        self.response_text = response_text
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "output": {
                "message": {
                    "content": [{"text": self.response_text}]
                }
            }
        }


def test_bedrock_adapter_parses_structured_proposal():
    response = {
        "action": "save",
        "memory_type": "commitment",
        "content": "finish the evaluation by Friday",
        "evidence": "I promised to finish the evaluation by Friday.",
        "confidence": 0.95,
        "reason": None,
    }
    client = FakeBedrockClient(json.dumps(response))
    proposer = BedrockMemoryProposer(client, "test-model")

    proposal = proposer.propose(
        "I promised to finish the evaluation by Friday."
    )

    assert proposal.action == "save"
    assert proposal.memory_type == "commitment"
    assert len(client.calls) == 1
    assert client.calls[0]["inferenceConfig"]["temperature"] == 0


def test_bedrock_adapter_rejects_invalid_json():
    client = FakeBedrockClient("not json")
    proposer = BedrockMemoryProposer(client, "test-model")

    with pytest.raises(ValueError, match="invalid JSON"):
        proposer.propose("I promised to finish the evaluation.")


def test_bedrock_adapter_rejects_invalid_proposal():
    response = {
        "action": "delete_everything",
        "memory_type": "commitment",
        "content": "Finish the project",
        "evidence": "I promised to finish the project.",
        "confidence": 0.9,
        "reason": None,
    }
    client = FakeBedrockClient(json.dumps(response))
    proposer = BedrockMemoryProposer(client, "test-model")

    with pytest.raises(ValueError):
        proposer.propose("I promised to finish the project.")


def test_bedrock_adapter_rejects_empty_input():
    client = FakeBedrockClient("{}")
    proposer = BedrockMemoryProposer(client, "test-model")

    with pytest.raises(ValueError, match="cannot be empty"):
        proposer.propose("  ")

    assert client.calls == []
