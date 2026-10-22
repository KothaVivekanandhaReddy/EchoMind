
import tempfile
from pathlib import Path
from echomind.sources import create_source, initialize_source_table
from echomind.confirmations import (
    create_pending_confirmation,
    confirm_and_save_memory,
    get_pending_confirmation,
)
from echomind.memory_service import get_memory_with_evidence


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        pending = create_pending_confirmation(
            "I should finish the atomic confirmation test.",
            db_path=db_path,
        )

        result = confirm_and_save_memory(
            pending.confirmation_id,
            db_path=db_path,
        )
        assert result["saved"] is True

        record = get_memory_with_evidence(
            result["memory_id"],
            db_path,
        )
        assert record is not None
        assert record["evidence_available"] is True
        assert record["evidence"].text == (
            "I should finish the atomic confirmation test."
        )

        resolved = get_pending_confirmation(
            pending.confirmation_id,
            db_path=db_path,
        )
        assert resolved is not None
        assert resolved.status == "confirmed"

        duplicate = confirm_and_save_memory(
            pending.confirmation_id,
            db_path=db_path,
        )
        assert duplicate["saved"] is False

    print("Atomic confirmation tests passed.")


if __name__ == "__main__":
    main()
