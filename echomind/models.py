
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


ALLOWED_TYPES = {
    "fact",
    "preference",
    "goal",
    "decision",
    "commitment",
}

ALLOWED_STATUSES = {
    "active",
    "superseded",
    "deleted",
}


@dataclass
class Memory: #represents a single structured memory using our six agreed fields.
    id: str
    type: str
    content: str
    source: str
    created_at: str
    status: str = "active"

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("Memory ID cannot be empty.")

        if self.type not in ALLOWED_TYPES:
            raise ValueError(f"Invalid memory type: {self.type}")

        if not self.content.strip():
            raise ValueError("Memory content cannot be empty.")

        if not self.source.strip():
            raise ValueError("Memory source cannot be empty.")

        try:
            datetime.fromisoformat(
                self.created_at.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError("Invalid created_at timestamp.") from exc

        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid memory status: {self.status}")


def create_memory( #generates a unique identifier and UTC timestamp
    memory_type: str,
    content: str,
    source: str,
) -> Memory:
    memory = Memory(
        id=f"mem_{uuid4().hex}",
        type=memory_type,
        content=content,
        source=source,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    memory.validate()
    return memory
