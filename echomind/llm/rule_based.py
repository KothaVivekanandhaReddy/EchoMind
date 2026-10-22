
from echomind.extractor import assess_memory_text
from echomind.llm.interface import MemoryProposal


class RuleBasedProposer:
    """Use the existing deterministic policy as the initial proposer."""

    def propose(self, text: str) -> MemoryProposal:
        assessment = assess_memory_text(text)
        action = assessment["action"]

        if action == "save":
            extracted = assessment["memory"]
            proposal = MemoryProposal(
                action="save",
                memory_type=extracted.memory_type,
                content=extracted.content,
                evidence=extracted.evidence,
                confidence=extracted.confidence,
            )
        elif action == "confirm":
            proposal = MemoryProposal(
                action="confirm",
                reason=assessment.get("reason"),
            )
        else:
            proposal = MemoryProposal(
                action="ignore",
                reason=assessment.get("reason"),
            )

        proposal.validate()
        return proposal
