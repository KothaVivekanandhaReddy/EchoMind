
import os

from echomind.llm.bedrock import (
    BedrockMemoryProposer,
    create_bedrock_client,
)
from echomind.llm.rule_based import RuleBasedProposer


def create_proposer(
    provider: str | None = None,
    model_id: str | None = None,
    region_name: str | None = None,
    bedrock_client=None,
):
    """Create the configured proposer without giving it storage access."""
    provider = (
        provider or os.getenv("ECHOMIND_LLM_PROVIDER", "rule_based")
    ).strip().lower()

    if provider == "rule_based":
        return RuleBasedProposer()

    if provider == "bedrock":
        model_id = model_id or os.getenv("ECHOMIND_BEDROCK_MODEL_ID")
        region_name = (
            region_name or os.getenv("AWS_REGION") or "us-east-1"
        )

        if not model_id or not model_id.strip():
            raise ValueError(
                "Set ECHOMIND_BEDROCK_MODEL_ID to use the Bedrock provider."
            )

        client = bedrock_client or create_bedrock_client(region_name)
        return BedrockMemoryProposer(client, model_id)

    raise ValueError(
        f"Unsupported ECHOMIND_LLM_PROVIDER: {provider!r}. "
        "Choose 'rule_based' or 'bedrock'."
    )
