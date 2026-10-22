
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from contextlib import closing


DEFAULT_DB_PATH = Path("data/echomind.db")


@dataclass
class SourceEvidence:
    source_id: str
    text: str
    captured_at: str

    def validate(self) -> None:
        if not self.source_id.strip():
            raise ValueError("Source ID cannot be empty.")

        if not self.text.strip():
            raise ValueError("Source text cannot be empty.")

        try:
            datetime.fromisoformat(
                self.captured_at.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError("Invalid captured_at timestamp.") from exc


def create_source(source_id: str, text: str) -> SourceEvidence:
    source = SourceEvidence(
        source_id=source_id,
        text=text,
        captured_at=datetime.now(timezone.utc).isoformat(),
    )
    source.validate()
    return source


def initialize_source_table(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    source_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    captured_at TEXT NOT NULL
                )
            """)


def save_source(
    source: SourceEvidence,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    source.validate()
    initialize_source_table(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute("""
                INSERT INTO sources (source_id, text, captured_at)
                VALUES (?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    text = excluded.text,
                    captured_at = excluded.captured_at
            """, (source.source_id, source.text, source.captured_at))


def get_source(
    source_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> SourceEvidence | None:
    initialize_source_table(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            row = connection.execute(
                "SELECT * FROM sources WHERE source_id = ?",
                (source_id,),
            ).fetchone()

    if row is None:
        return None

    source = SourceEvidence(
        source_id=row["source_id"],
        text=row["text"],
        captured_at=row["captured_at"],
    )
    source.validate()
    return source
