
import subprocess
import sys
import tempfile
from pathlib import Path

from echomind.models import create_memory
from echomind.storage import save_memory


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "persistence_test.db"

    memory = create_memory(
        memory_type="commitment",
        content="Submit the hackathon project",
        source="persistence_test",
    )

    # Process 1: save the memory, then exit.
    save_memory(memory, db_path)
    print(f"Saved memory ID: {memory.id}")

    # Process 2: start a fresh Python interpreter and retrieve it.
    retrieval_script = """
import sys
from pathlib import Path
from echomind.storage import get_memory

db_path = Path(sys.argv[1])
memory_id = sys.argv[2]

memory = get_memory(memory_id, db_path)

if memory is None:
    raise SystemExit("FAIL: Memory was not found.")

print(f"Retrieved content: {memory.content}")
print(f"Retrieved status: {memory.status}")
"""

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            retrieval_script,
            str(db_path),
            memory.id,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    print(result.stdout, end="")

    assert "Submit the hackathon project" in result.stdout
    assert "Retrieved status: active" in result.stdout

    print("Cross-process persistence test passed.")
