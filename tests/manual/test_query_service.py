
import tempfile
from pathlib import Path

from echomind.query_service import answer_memory_query
from echomind.memory_service import remember


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "query_test.db"

    remember(
        memory_type="commitment",
        content="Finish the RAG evaluation project",
        source_id="conversation_001",
        source_text=(
            "I promised to finish the RAG evaluation project by Friday."
        ),
        db_path=db_path,
    )

    result = answer_memory_query(
        query="finish RAG project",
        db_path=db_path,
        memory_type="commitment",
    )

    assert result["found"] is True
    assert result["count"] == 1
    assert result["results"][0]["content"] == (
        "Finish the RAG evaluation project"
    )
    assert result["results"][0]["evidence_available"] is True
    assert "by Friday" in result["results"][0]["evidence"]

    missing = answer_memory_query(
        query="dentist appointment",
        db_path=db_path,
    )

    assert missing["found"] is False
    assert missing["count"] == 0
    assert missing["results"] == []

    print("Query service tests passed.")
