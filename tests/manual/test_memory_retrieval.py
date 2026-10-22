
import tempfile
from pathlib import Path
from contextlib import closing
from echomind.models import create_memory
from echomind.storage import save_memory, search_memories


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "retrieval_test.db"

    memories = [
        create_memory(
            "commitment",
            "Finish the RAG evaluation project",
            "test_001",
        ),
        create_memory(
            "commitment",
            "Submit the hackathon project",
            "test_002",
        ),
        create_memory(
            "decision",
            "Use SQLite for persistent memory storage",
            "test_003",
        ),
        create_memory(
            "commitment",
            "Finish the database testing report",
            "test_004",
        ),
    ]

    for memory in memories:
        save_memory(memory, db_path)

    # Search should find relevant memories.
    results = search_memories("finish project", db_path)

    assert len(results) == 3
    assert results[0].content == "Finish the RAG evaluation project"

    remaining_contents = {memory.content for memory in results[1:]}

    assert remaining_contents == {
        "Submit the hackathon project",
        "Finish the database testing report",
    }

    # Type filtering should return commitments only.
    commitments = search_memories(
        "storage",
        db_path,
        memory_type="commitment",
    )
    assert all(memory.type == "commitment" for memory in commitments)

    # Inactive memories should not appear.
    memories[0].status = "superseded"
    # Persist the status change directly for this test.
    import sqlite3

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute(
                "UPDATE memories SET status = ? WHERE id = ?",
                ("superseded", memories[0].id),
           )

    results_after_update = search_memories("RAG evaluation", db_path)
    assert all(memory.id != memories[0].id for memory in results_after_update)

    print("Memory retrieval tests passed.")
