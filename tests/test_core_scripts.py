
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CORE_SCRIPTS = [
    "test_memory_model.py",
    "test_memory_storage.py",
    "test_memory_persistence.py",
    "test_memory_retrieval.py",
    "test_memory_date_search.py",
    "test_sources.py",
    "test_memory_service.py",
    "test_query_service.py",
    "test_intent_retrieval.py",
    "test_time_parser.py",
    "test_temporal_query.py",
    "test_extractor.py",
    "test_extractor_safety.py",
    "test_confirmation_policy.py",
    "test_confirmations.py",
    "test_atomic_confirmation.py",
]


@pytest.mark.parametrize("script_name", CORE_SCRIPTS)
def test_core_script(script_name):
    result = subprocess.run(
        [sys.executable, script_name],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, (
        f"{script_name} failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
