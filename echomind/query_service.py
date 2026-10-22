
from pathlib import Path

from echomind.memory_service import get_memory_with_evidence
from echomind.storage import search_memories
from echomind.time_parser import parse_time_range
from datetime import datetime

STOP_WORDS = {
    "a", "an", "the", "i", "me", "my", "we", "our", "you", "your",
    "what", "which", "who", "when", "where", "why", "how",
    "did", "do", "does", "have", "has", "had", "was", "were",
    "is", "are", "am", "to", "of", "for", "in", "on", "at",
    "it", "this", "that", "with", "about", "from", "last",
    "week", "month", "day", "please", "tell", "show", "find",
}

INTENT_TERMS = {
    "commitment": {
        "promise", "promised", "commitment", "committed",
        "finish", "complete", "deliver", "deadline", "owe",
    },
    "decision": {
        "decide", "decides", "decided", "decision",
        "decisions", "choose", "chose", "chosen"
    },
    "preference": {"prefer", "preference", "like", "likes"},
    "goal": {"goal", "aim", "target", "want", "plan"},
}


def infer_memory_type(query: str) -> str | None:
    """Infer a memory type from common natural-language intent terms."""
    words = set(query.casefold().replace("?", "").replace(",", "").split())

    for memory_type, terms in INTENT_TERMS.items():
        if words & terms:
            return memory_type

    return None


def normalize_search_query(query: str) -> str:
    """Remove common conversational filler while preserving search terms."""
    words = query.casefold().replace("?", "").replace(",", "").split()
    useful_words = [word for word in words if word not in STOP_WORDS]

    return " ".join(useful_words) if useful_words else query.strip()


def answer_memory_query(
    query: str,
    db_path: Path,
    memory_type: str | None = None,
    limit: int = 5,
    now: datetime | None = None,
) -> dict:
    """Return matching memories with their original source evidence."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    effective_type = memory_type or infer_memory_type(query)
    search_query = normalize_search_query(query)

    created_after, created_before = parse_time_range(query, now=now)

    memories = search_memories(
        query=search_query,
        db_path=db_path,
        memory_type=effective_type,
        limit=limit,
        created_after=created_after,
        created_before=created_before,
    )

    results = []

    for memory in memories:
        record = get_memory_with_evidence(memory.id, db_path)

        if record is None:
            continue

        evidence = record["evidence"]

        results.append({
            "memory_id": memory.id,
            "type": memory.type,
            "content": memory.content,
            "status": memory.status,
            "created_at": memory.created_at,
            "source_id": memory.source,
            "evidence": evidence.text if evidence else None,
            "evidence_available": record["evidence_available"],
        })

    return {
        "query": query,
        "inferred_type": effective_type,
        "search_query": search_query,
        "found": bool(results),
        "count": len(results),
        "results": results,
        "message": (
            "Matching memories found."
            if results
            else "No matching memories found. No answer can be verified."
        ),
    }
