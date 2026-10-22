
import tempfile
from pathlib import Path

from echomind.sources import create_source, save_source, get_source


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "sources_test.db"

    source = create_source(
        "conversation_001",
        "I promised to finish the RAG evaluation project by Friday.",
    )

    save_source(source, db_path)
    retrieved = get_source(source.source_id, db_path)

    assert retrieved is not None
    assert retrieved.source_id == source.source_id
    assert retrieved.text == source.text
    assert retrieved.captured_at == source.captured_at

    assert get_source("missing_source", db_path) is None

    print("Source evidence tests passed.")
