
import subprocess
import sys
from pathlib import Path
import socket
import time
import pytest
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MCP_SCRIPTS = [
    "test_mcp_connection.py",
    "test_mcp_extraction.py",
    "test_mcp_confirmation.py",
    "test_mcp_confirm_save.py",
]

@pytest.fixture(scope="module", autouse=True)
def mcp_server():
    """Start the MCP server for integration tests and clean it up afterward."""
    if os.getenv("ECHOMIND_RUN_LIVE_TESTS") != "1":
        pytest.skip(
            "Live MCP/Bedrock tests disabled by default. "
            "Set ECHOMIND_RUN_LIVE_TESTS=1 to enable them."
        )
    host = "127.0.0.1"
    port = 8000

    def is_server_ready():
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            return False

    # Reuse a server that is already running.
    if is_server_ready():
        yield
        return

    import subprocess

    process = subprocess.Popen(
        [sys.executable, "-m", "echomind.server"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.monotonic() + 15

        while time.monotonic() < deadline:
            if is_server_ready():
                break

            if process.poll() is not None:
                pytest.fail("MCP server exited before becoming ready.")

            time.sleep(0.25)
        else:
            pytest.fail("MCP server did not become ready within 15 seconds.")

        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.mark.parametrize("script_name", MCP_SCRIPTS)
def test_mcp_script(script_name):
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
