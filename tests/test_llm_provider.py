
import pytest

from echomind.llm.provider import create_proposer
from echomind.llm.rule_based import RuleBasedProposer
from echomind.llm.bedrock import BedrockMemoryProposer


class FakeBedrockClient:
    def converse(self, **kwargs):
        raise AssertionError("This test must not make a model call.")


def test_rule_based_is_the_default(monkeypatch):
    monkeypatch.delenv("ECHOMIND_LLM_PROVIDER", raising=False)

    proposer = create_proposer()

    assert isinstance(proposer, RuleBasedProposer)


def test_provider_can_be_selected_with_environment(monkeypatch):
    monkeypatch.setenv("ECHOMIND_LLM_PROVIDER", "rule_based")

    proposer = create_proposer()

    assert isinstance(proposer, RuleBasedProposer)


def test_bedrock_requires_model_id(monkeypatch):
    monkeypatch.delenv("ECHOMIND_BEDROCK_MODEL_ID", raising=False)

    with pytest.raises(ValueError, match="ECHOMIND_BEDROCK_MODEL_ID"):
        create_proposer(provider="bedrock")


def test_bedrock_provider_accepts_injected_client():
    proposer = create_proposer(
        provider="bedrock",
        model_id="test-model",
        bedrock_client=FakeBedrockClient(),
    )

    assert isinstance(proposer, BedrockMemoryProposer)


def test_unknown_provider_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        create_proposer(provider="unknown")
