
from pathlib import Path
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

from echomind.confirmations import (
    create_pending_confirmation,
    get_pending_confirmation,
    resolve_confirmation,
    confirm_and_save_memory,
)
from echomind.extractor import assess_memory_text
from echomind.llm.policy import validate_proposal
from echomind.llm.provider import create_proposer
from echomind.memory_service import (
    remember,
    get_memory_with_evidence,
)
from echomind.query_service import answer_memory_query


mcp = FastMCP("EchoMind")

DB_PATH = Path("data/echomind.db")
proposer = create_proposer()


@mcp.tool()
def remember_memory(
    memory_type: str,
    content: str,
    source_id: str,
    source_text: str,
) -> dict:
    """Save a memory and its original supporting source evidence."""
    allowed_types = {
        "fact",
        "preference",
        "goal",
        "decision",
        "commitment",
    }

    if memory_type not in allowed_types:
        raise ValueError(
            f"Invalid memory_type. Choose one of: {sorted(allowed_types)}"
        )

    memory = remember(
        memory_type=memory_type,
        content=content,
        source_id=source_id,
        source_text=source_text,
        db_path=DB_PATH,
    )

    return {
        "saved": True,
        "memory_id": memory.id,
        "type": memory.type,
        "content": memory.content,
        "source_id": memory.source,
    }


@mcp.tool()
def search_memory(
    query: str,
    memory_type: str | None = None,
    limit: int = 5,
) -> dict:
    """Search saved memories and return matching source evidence."""
    return answer_memory_query(
        query=query,
        db_path=DB_PATH,
        memory_type=memory_type,
        limit=limit,
    )


@mcp.tool()
def get_memory_evidence(memory_id: str) -> dict:
    """Retrieve a saved memory and its supporting source text."""
    record = get_memory_with_evidence(memory_id, DB_PATH)

    if record is None:
        return {
            "found": False,
            "message": "Memory not found.",
        }

    memory = record["memory"]
    evidence = record["evidence"]

    return {
        "found": True,
        "memory_id": memory.id,
        "type": memory.type,
        "content": memory.content,
        "status": memory.status,
        "source_id": memory.source,
        "evidence_available": record["evidence_available"],
        "evidence": evidence.text if evidence else None,
    }


@mcp.tool()
def remember_from_text(text: str) -> dict:
    """Classify input deterministically, then validate any LLM proposal."""
    if not text.strip():
        return {
            "saved": False,
            "action": "ignore",
            "reason": "empty_input",
            "message": "Please provide text to analyze.",
        }

    # The deterministic application policy is authoritative.
    assessment = assess_memory_text(text)

    if assessment["action"] == "confirm":
        pending = create_pending_confirmation(
            original_text=text.strip(),
            memory_type="commitment",
            db_path=DB_PATH,
        )

        return {
            "saved": False,
            "action": "confirm",
            "confirmation_id": pending.confirmation_id,
            "message": (
                "Should I remember this as a commitment? "
                "Confirm using the provided confirmation ID."
            ),
            "original_text": pending.original_text,
        }

    if assessment["action"] == "ignore":
        return {
            "saved": False,
            "action": "ignore",
            "reason": assessment["reason"],
            "message": "No memory was saved.",
        }

    # Only explicitly supported input reaches the proposer.
    proposal = proposer.propose(text)

    # The model cannot override the deterministic policy.
    validate_proposal(text, proposal)

    if proposal.action != "save":
        return {
            "saved": False,
            "action": proposal.action,
            "reason": proposal.reason or "proposal_not_saveable",
            "message": "No memory was saved.",
        }

    # Only the application layer writes to storage.
    source_id = f"conversation_{uuid4().hex}"

    memory = remember(
        memory_type=proposal.memory_type,
        content=proposal.content,
        source_id=source_id,
        source_text=proposal.evidence,
        db_path=DB_PATH,
    )

    return {
        "saved": True,
        "action": "save",
        "memory_id": memory.id,
        "type": memory.type,
        "content": memory.content,
        "source_id": memory.source,
        "evidence": proposal.evidence,
        "confidence": proposal.confidence,
    }


@mcp.tool()
def confirm_memory(
    confirmation_id: str,
    confirmed: bool,
) -> dict:
    """Confirm or decline a pending memory request exactly once."""
    pending = get_pending_confirmation(
        confirmation_id,
        db_path=DB_PATH,
    )

    if pending is None:
        return {
            "saved": False,
            "action": "ignore",
            "reason": "confirmation_not_found",
            "message": "Confirmation request not found.",
        }

    if pending.status != "pending":
        return {
            "saved": False,
            "action": "ignore",
            "reason": "confirmation_already_resolved",
            "message": (
                f"This confirmation has already been {pending.status}."
            ),
        }

    if not confirmed:
        resolved = resolve_confirmation(
            confirmation_id,
            False,
            db_path=DB_PATH,
        )

        if not resolved:
            return {
                "saved": False,
                "action": "ignore",
                "reason": "confirmation_already_resolved",
                "message": "This confirmation was already resolved.",
            }

        return {
            "saved": False,
            "action": "ignore",
            "message": "Confirmation declined. No memory was saved.",
        }

    result = confirm_and_save_memory(
        confirmation_id,
        db_path=DB_PATH,
    )

    if not result["saved"]:
        return {
            **result,
            "action": "ignore",
            "message": "This confirmation is no longer pending.",
        }

    return {
        **result,
        "action": "save",
        "message": "Confirmation accepted and memory saved.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
