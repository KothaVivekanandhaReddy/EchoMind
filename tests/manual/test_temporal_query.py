
import tempfile
from pathlib import Path

from echomind.memory_service import remember
from echomind.query_service import answer_memory_query
from datetime import datetime
from zoneinfo import ZoneInfo


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "temporal_test.db"

    last_week = remember(
        "commitment",
        "Finish the RAG evaluation project",
        "conversation_old",
        "I promised to finish the RAG evaluation project by Friday.",
        db_path,
    )
    last_week.created_at = "2026-10-06T10:00:00+00:00"

    this_week = remember(
        "commitment",
        "Finish the hackathon submission",
        "conversation_new",
        "I promised to finish the hackathon submission.",
        db_path,
    )
    this_week.created_at = "2026-10-12T06:00:00+00:00"

    # Set controlled timestamps directly for this test.
    import sqlite3
    from contextlib import closing

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.executemany(
                "UPDATE memories SET created_at = ? WHERE id = ?",
                [
                    (last_week.created_at, last_week.id),
                    (this_week.created_at, this_week.id),
                ],
            )
    # Fix the clock so the test always uses October 12, 2026.
    fixed_now = datetime(
        2026, 10, 12, 12, 0,
        tzinfo=ZoneInfo("Asia/Kolkata"),
    )

    result = answer_memory_query(
        "What did I promise to finish last week?",
        db_path,
        limit=10,
        now=fixed_now,
    )

    print("Temporal query results:")
    for item in result["results"]:
        print("-", item["content"])



    assert result["results"][0]["content"] == (
        "Finish the RAG evaluation project"
    )
    print("Temporal query integration test passed.")