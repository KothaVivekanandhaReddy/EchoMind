
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from contextlib import closing
from uuid import uuid4
from echomind.models import create_memory
from echomind.sources import create_source, initialize_source_table


DEFAULT_DB_PATH = Path("data/echomind.db")


@dataclass
class PendingConfirmation:
    confirmation_id: str
    original_text: str
    memory_type: str
    status: str
    created_at: str

    def validate(self) -> None:
        if not self.confirmation_id.strip():
            raise ValueError("Confirmation ID cannot be empty.")

        if not self.original_text.strip():
            raise ValueError("Original text cannot be empty.")

        if self.memory_type not in {
            "fact", "preference", "goal", "decision", "commitment"
        }:
            raise ValueError("Invalid memory type.")

        if self.status not in {"pending", "confirmed", "declined"}:
            raise ValueError("Invalid confirmation status.")

        try:
            datetime.fromisoformat(
                self.created_at.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError("Invalid created_at timestamp.") from exc


def initialize_confirmation_table(
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS pending_confirmations (
                    confirmation_id TEXT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    status TEXT NOT NULL
                        CHECK (status IN (
                            'pending', 'confirmed', 'declined'
                        )),
                    created_at TEXT NOT NULL
                )
            """)


def create_pending_confirmation(
    original_text: str,
    memory_type: str = "commitment",
    db_path: Path = DEFAULT_DB_PATH,
) -> PendingConfirmation:
    if not original_text.strip():
        raise ValueError("Original text cannot be empty.")

    confirmation = PendingConfirmation(
        confirmation_id=f"confirm_{uuid4().hex}",
        original_text=original_text.strip(),
        memory_type=memory_type,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    confirmation.validate()

    initialize_confirmation_table(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute("""
                INSERT INTO pending_confirmations (
                    confirmation_id, original_text, memory_type,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                confirmation.confirmation_id,
                confirmation.original_text,
                confirmation.memory_type,
                confirmation.status,
                confirmation.created_at,
            ))

    return confirmation


def get_pending_confirmation(
    confirmation_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> PendingConfirmation | None:
    initialize_confirmation_table(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            row = connection.execute("""
                SELECT * FROM pending_confirmations
                WHERE confirmation_id = ?
            """, (confirmation_id,)).fetchone()

    if row is None:
        return None

    confirmation = PendingConfirmation(
        confirmation_id=row["confirmation_id"],
        original_text=row["original_text"],
        memory_type=row["memory_type"],
        status=row["status"],
        created_at=row["created_at"],
    )
    confirmation.validate()
    return confirmation


def resolve_confirmation(
    confirmation_id: str,
    confirmed: bool,
    db_path: Path = DEFAULT_DB_PATH,
) -> bool:
    """Resolve a pending request once; return False if it is not pending."""
    initialize_confirmation_table(db_path)

    new_status = "confirmed" if confirmed else "declined"

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.execute("""
                UPDATE pending_confirmations
                SET status = ?
                WHERE confirmation_id = ? AND status = 'pending'
            """, (new_status, confirmation_id))

    return cursor.rowcount == 1


def confirm_and_save_memory(
    confirmation_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict:
    """Atomically confirm a pending request and save its memory and evidence."""
    from echomind.storage import initialize_db

    initialize_confirmation_table(db_path)
    initialize_db(db_path)
    initialize_source_table(db_path)

    with closing(sqlite3.connect(db_path, timeout=10)) as connection:
        connection.row_factory = sqlite3.Row

        with connection:
            pending = connection.execute(
                """
                SELECT * FROM pending_confirmations
                WHERE confirmation_id = ? AND status = 'pending'
                """,
                (confirmation_id,),
            ).fetchone()

            if pending is None:
                return {
                    "saved": False,
                    "reason": "confirmation_not_pending",
                }

            source_id = f"conversation_{uuid4().hex}"
            source = create_source(source_id, pending["original_text"])
            memory = create_memory(
                memory_type=pending["memory_type"],
                content=pending["original_text"],
                source=source_id,
            )

            connection.execute(
                """
                INSERT INTO sources (source_id, text, captured_at)
                VALUES (?, ?, ?)
                """,
                (source.source_id, source.text, source.captured_at),
            )

            connection.execute(
                """
                INSERT INTO memories (
                    id, type, content, source, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.id,
                    memory.type,
                    memory.content,
                    memory.source,
                    memory.created_at,
                    memory.status,
                ),
            )

            cursor = connection.execute(
                """
                UPDATE pending_confirmations
                SET status = 'confirmed'
                WHERE confirmation_id = ? AND status = 'pending'
                """,
                (confirmation_id,),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Confirmation was resolved concurrently."
                )

    return {
        "saved": True,
        "memory_id": memory.id,
        "type": memory.type,
        "content": memory.content,
        "source_id": memory.source,
        "evidence": source.text,
        "confirmed": True,
    }
