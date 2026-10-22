
import tempfile
from pathlib import Path

from echomind.models import create_memory
from echomind.storage import save_memory, get_memory


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "test.db"

    memory = create_memory(
        memory_type="commitment",
        content="Finish the RAG evaluation project",
        source="input_001",
    )

    # Save the memory.
    save_memory(memory, db_path)

    # Retrieve it from SQLite.
    retrieved = get_memory(memory.id, db_path)

    assert retrieved is not None
    assert retrieved.id == memory.id
    assert retrieved.type == "commitment"
    assert retrieved.content == "Finish the RAG evaluation project"
    assert retrieved.source == "input_001"
    assert retrieved.created_at == memory.created_at
    assert retrieved.status == "active"

    # Confirm missing IDs return None.
    assert get_memory("missing_id", db_path) is None

    print("Memory saved and retrieved successfully.")
    print(retrieved)
    print("\nMemory storage tests passed.")
