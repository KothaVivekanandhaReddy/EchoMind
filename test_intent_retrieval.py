
import tempfile
from pathlib import Path

from echomind.memory_service import remember
from echomind.query_service import answer_memory_query, infer_memory_type


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "intent_test.db"

    remember(
        memory_type="commitment",
        content="Finish the RAG evaluation project",
        source_id="conversation_001",
        source_text=(
            "I promised to finish the RAG evaluation project by Friday."
        ),
        db_path=db_path,
    )

    remember(
        memory_type="decision",
        content="Use SQLite for persistent memory storage",
        source_id="conversation_002",
        source_text="I decided to use SQLite for persistent memory storage.",
        db_path=db_path,
    )

    # Intent classification.
    assert infer_memory_type("What did I promise to finish?") == "commitment"
    assert infer_memory_type("What did we decide?") == "decision"
    assert infer_memory_type("Show me everything") is None

    # Natural-language query should find the commitment.
    result = answer_memory_query(
        "What did I promise to finish?",
        db_path,
    )

    assert result["found"] is True
    assert result["inferred_type"] == "commitment"
    assert result["count"] == 1
    assert result["results"][0]["content"] == (
        "Finish the RAG evaluation project"
    )
    assert result["results"][0]["evidence_available"] is True

    print("Intent-aware retrieval tests passed.")
