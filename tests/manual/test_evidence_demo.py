
import tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from echomind.memory_service import remember
from echomind.query_service import answer_memory_query


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "demo.db"

        original_text = (
            "I promised to finish the RAG evaluation project by Friday."
        )

        memory = remember(
            memory_type="commitment",
            content="Finish the RAG evaluation project",
            source_id="demo_commitment_001",
            source_text=original_text,
            db_path=db_path,
        )

        # Set a controlled date so this demo is repeatable.
        memory.created_at = "2026-10-06T10:00:00+00:00"

        import sqlite3
        from contextlib import closing

        with closing(sqlite3.connect(db_path)) as connection:
            with connection:
                connection.execute(
                    "UPDATE memories SET created_at = ? WHERE id = ?",
                    (memory.created_at, memory.id),
                )

        fixed_now = datetime(
            2026, 10, 12, 12, 0,
            tzinfo=ZoneInfo("Asia/Kolkata"),
        )

        result = answer_memory_query(
            "What did I promise to finish last week?",
            db_path=db_path,
            now=fixed_now,
        )

        assert result["count"] == 1, result
        item = result["results"][0]

        assert item["type"] == "commitment"
        assert item["content"] == "Finish the RAG evaluation project"
        assert item["evidence_available"] is True
        assert item["evidence"] == original_text

        print("\nEchoMind commitment recall demo")
        print(f"Question: {result['query']}")
        print(f"Commitment: {item['content']}")
        print(f"Original evidence: {item['evidence']}")
        print(f"Created at: {item['created_at']}")
        print("\nPASS: Retrieved the commitment with supporting evidence.")


if __name__ == "__main__":
    main()
