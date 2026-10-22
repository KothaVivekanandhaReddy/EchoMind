
from dataclasses import dataclass
from typing import Literal, Protocol


ProposalAction = Literal["save", "confirm", "ignore"]


@dataclass(frozen=True)
class MemoryProposal:
    action: ProposalAction
    memory_type: str | None = None
    content: str | None = None
    evidence: str | None = None
    confidence: float | None = None
    reason: str | None = None

    def validate(self) -> None:
        if self.action not in {"save", "confirm", "ignore"}:
            raise ValueError("Invalid proposal action.")

        allowed_types = {
            "fact", "preference", "goal", "decision", "commitment"
        }

        if self.memory_type is not None:
            if self.memory_type not in allowed_types:
                raise ValueError("Invalid proposed memory type.")

        if self.action == "save":
            if not self.memory_type or not self.content or not self.evidence:
                raise ValueError(
                    "Save proposals require type, content, and evidence."
                )

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError("Confidence must be between 0 and 1.")


class MemoryProposer(Protocol):
    """Contract implemented by rule-based and future LLM proposers."""

    def propose(self, text: str) -> MemoryProposal:
        """Return a candidate decision without saving anything."""
        ...
