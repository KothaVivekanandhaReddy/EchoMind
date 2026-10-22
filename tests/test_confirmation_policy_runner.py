
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_confirmation_policy_script():
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        str(PROJECT_ROOT)
        + os.pathsep
        + env.get("PYTHONPATH", "")
    )

    result = subprocess.run(
        [sys.executable, "test_confirmation_policy.py"],
        cwd=PROJECT_ROOT / "tests" / "manual",
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, (
        f"Script failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert "Confirmation policy tests passed." in result.stdout
