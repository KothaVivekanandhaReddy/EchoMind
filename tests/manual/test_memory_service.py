
import tempfile
from pathlib import Path

from echomind.memory_service import remember, get_memory_with_evidence


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "service_test.db"

    memory = remember(
        memory_type="commitment",
        content="Finish the RAG evaluation project",
        source_id="conversation_001",
        source_text=(
            "I promised to finish the RAG evaluation project by Friday."
        ),
        db_path=db_path,
    )

    result = get_memory_with_evidence(memory.id, db_path)

    assert result is not None
    assert result["memory"].content == "Finish the RAG evaluation project"
    assert result["evidence_available"] is True
    assert result["evidence"].text == (
        "I promised to finish the RAG evaluation project by Friday."
    )

    missing = get_memory_with_evidence("missing_id", db_path)
    assert missing is None

    print("Memory service and evidence-link tests passed.")
