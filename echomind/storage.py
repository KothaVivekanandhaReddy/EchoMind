
import sqlite3
from pathlib import Path
from contextlib import closing
from echomind.models import Memory


DEFAULT_DB_PATH = Path("data/echomind.db")


def initialize_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the database and memories table if they do not exist."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection:
         with connection:
            connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK (
                    type IN (
                        'fact',
                        'preference',
                        'goal',
                        'decision',
                        'commitment'
                    )
                ),
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN ('active', 'superseded', 'deleted')
                )
            )
        """)


def save_memory(
    memory: Memory,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Validate and persist a memory."""
    memory.validate()
    initialize_db(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
         with connection:
            connection.execute("""
                INSERT INTO memories (
                    id, type, content, source, created_at, status
                )
                VALUES (?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.type,
            memory.content,
            memory.source,
            memory.created_at,
            memory.status,
        ))


def get_memory(
    memory_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> Memory | None:
    """Retrieve a memory by ID, or return None if it does not exist."""
    initialize_db(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row

        with connection:
             row = connection.execute(
                  "SELECT * FROM memories WHERE id = ?",
                  (memory_id,),
             ).fetchone()

    if row is None:
        return None

    memory = Memory(
        id=row["id"],
        type=row["type"],
        content=row["content"],
        source=row["source"],
        created_at=row["created_at"],
        status=row["status"],
    )
    memory.validate()
    return memory


from datetime import datetime


def _timestamp_key(timestamp: str) -> float:
    """Convert an ISO timestamp to a numeric value for stable sorting."""
    value = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.timestamp()


def search_memories(
    query: str,
    db_path: Path = DEFAULT_DB_PATH,
    memory_type: str | None = None,
    limit: int = 10,
    created_after: str | None = None,
    created_before: str | None = None,
) -> list[Memory]:
    """Search active memories by keywords, with optional creation-date filters."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    initialize_db(db_path)

    keywords = {
        word.casefold().strip(".,!?;:\"'()[]{}")
        for word in query.split()
    }
    keywords.discard("")

    if not keywords:
        raise ValueError("Search query must contain a searchable word.")

    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row

        sql = "SELECT * FROM memories WHERE status = 'active'"
        params: list[str] = []

        if memory_type is not None:
            sql += " AND type = ?"
            params.append(memory_type)

        if created_after is not None:
            sql += " AND created_at >= ?"
            params.append(created_after)

        if created_before is not None:
            sql += " AND created_at < ?"
            params.append(created_before)

        sql += " ORDER BY created_at DESC, id ASC"

        with connection:
            rows = connection.execute(sql, params).fetchall()

    scored: list[tuple[int, str, Memory]] = []

    for row in rows:
        memory = Memory(
            id=row["id"],
            type=row["type"],
            content=row["content"],
            source=row["source"],
            created_at=row["created_at"],
            status=row["status"],
        )
        memory.validate()

        content_words = {
            word.casefold().strip(".,!?;:\"'()[]{}")
            for word in memory.content.split()
        }

        score = len(keywords & content_words)

        if score > 0:
            scored.append((score, memory.created_at, memory))

    # Highest keyword score first, then newest memory, then stable ID.
    scored.sort(key=lambda item: (-item[0], -_timestamp_key(item[1]), item[2].id))

    return [memory for _, _, memory in scored[:limit]]
