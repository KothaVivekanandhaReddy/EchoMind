
import tempfile
from pathlib import Path

from echomind.confirmations import (
    create_pending_confirmation,
    get_pending_confirmation,
    resolve_confirmation,
)


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        pending = create_pending_confirmation(
            "I should finish the evaluation.",
            db_path=db_path,
        )

        assert pending.status == "pending"

        loaded = get_pending_confirmation(
            pending.confirmation_id,
            db_path=db_path,
        )
        assert loaded is not None
        assert loaded.original_text == "I should finish the evaluation."
        assert loaded.status == "pending"

        assert resolve_confirmation(
            pending.confirmation_id,
            True,
            db_path=db_path,
        ) is True

        assert resolve_confirmation(
            pending.confirmation_id,
            True,
            db_path=db_path,
        ) is False

        resolved = get_pending_confirmation(
            pending.confirmation_id,
            db_path=db_path,
        )
        assert resolved is not None
        assert resolved.status == "confirmed"

        assert get_pending_confirmation(
            "confirm_does_not_exist",
            db_path=db_path,
        ) is None

    print("Pending-confirmation storage tests passed.")


if __name__ == "__main__":
    main()
