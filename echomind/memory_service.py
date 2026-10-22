
from pathlib import Path

from echomind.models import Memory, create_memory
from echomind.sources import create_source, save_source, get_source
from echomind.storage import save_memory, get_memory


def remember(
    memory_type: str,
    content: str,
    source_id: str,
    source_text: str,
    db_path: Path,
) -> Memory:
    """Save source evidence and the memory that was derived from it."""
    source = create_source(source_id, source_text)

    memory = create_memory(
        memory_type=memory_type,
        content=content,
        source=source_id,
    )

    # Save evidence first so the memory never points to a source
    # that has not been stored yet.
    save_source(source, db_path)
    save_memory(memory, db_path)

    return memory


def get_memory_with_evidence(
    memory_id: str,
    db_path: Path,
) -> dict | None:
    """Return a memory and its source evidence, if both exist."""
    memory = get_memory(memory_id, db_path)

    if memory is None:
        return None

    source = get_source(memory.source, db_path)

    return {
        "memory": memory,
        "evidence": source,
        "evidence_available": source is not None,
    }
