
import tempfile
from pathlib import Path

from echomind.models import create_memory
from echomind.storage import save_memory, search_memories


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "date_search_test.db"

    old_memory = create_memory(
        "commitment",
        "Finish the RAG evaluation project",
        "test_old",
    )
    current_memory = create_memory(
        "commitment",
        "Finish the hackathon submission",
        "test_current",
    )

    # Give the records controlled timestamps so the test is repeatable.
    old_memory.created_at = "2026-10-01T10:00:00+00:00"
    current_memory.created_at = "2026-10-12T10:00:00+00:00"

    save_memory(old_memory, db_path)
    save_memory(current_memory, db_path)

    results = search_memories(
        "finish",
        db_path,
        memory_type="commitment",
        created_after="2026-10-01T00:00:00+00:00",
        created_before="2026-10-08T00:00:00+00:00",
    )

    assert len(results) == 1
    assert results[0].id == old_memory.id

    print("Date-filter retrieval test passed.")
