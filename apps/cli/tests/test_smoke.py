"""
Smoke tests for E2B Sandbox CLI.

These tests verify basic functionality:
- Sandbox creation
- Command execution
- File operations
- Sandbox cleanup

Requirements:
- E2B_API_KEY must be set in .env file
"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repository root
root_dir = Path(__file__).parent.parent.parent.parent
load_dotenv(root_dir / ".env")


def test_env_loaded():
    """Verify E2B_API_KEY is loaded from .env"""
    api_key = os.getenv("E2B_API_KEY")
    assert api_key is not None, "E2B_API_KEY not found in .env file"
    assert api_key.startswith("e2b_"), "E2B_API_KEY should start with 'e2b_'"


@pytest.fixture
def sandbox():
    """Create a sandbox for testing, clean up after"""
    from e2b import Sandbox

    sbx = Sandbox.create(timeout=300)
    print(f"\n✓ Created sandbox: {sbx.sandbox_id}")

    yield sbx

    # Cleanup
    try:
        sbx.kill()
        print(f"✓ Killed sandbox: {sbx.sandbox_id}")
    except Exception as e:
        print(f"⚠ Warning: Failed to kill sandbox: {e}")


def test_sandbox_creation(sandbox):
    """Test basic sandbox creation"""
    assert sandbox.sandbox_id is not None
    assert len(sandbox.sandbox_id) > 0
    print(f"✓ Sandbox ID: {sandbox.sandbox_id}")


def test_command_execution(sandbox):
    """Test executing a simple command"""
    result = sandbox.commands.run("echo 'Hello from E2B'")
    assert result.exit_code == 0
    assert "Hello from E2B" in result.stdout
    print(f"✓ Command executed: {result.stdout.strip()}")


def test_file_write_and_read(sandbox):
    """Test writing and reading files"""
    test_content = "Hello from test!"
    test_path = "/home/user/test.txt"

    # Write file
    sandbox.files.write(test_path, test_content)
    print(f"✓ Wrote file: {test_path}")

    # Read file back
    content = sandbox.files.read(test_path)
    assert content == test_content
    print(f"✓ Read file: {content}")


def test_file_operations(sandbox):
    """Test file operations: mkdir, exists, list, remove"""
    # Create directory
    test_dir = "/home/user/testdir"
    sandbox.files.make_dir(test_dir)
    print(f"✓ Created directory: {test_dir}")

    # Check file exists
    exists = sandbox.files.exists(test_dir)
    assert exists is True
    print(f"✓ Directory exists: {exists}")

    # List files
    files = sandbox.files.list("/home/user")
    dir_names = [f.name for f in files]
    assert "testdir" in dir_names
    print(f"✓ Listed files: {dir_names}")

    # Remove directory
    sandbox.files.remove(test_dir)
    print(f"✓ Removed directory: {test_dir}")

    # Verify removed
    exists = sandbox.files.exists(test_dir)
    assert exists is False


def test_python_execution(sandbox):
    """Test running Python code"""
    # Write a simple Python script
    script = """
print("Python test successful")
import sys
print(f"Python version: {sys.version.split()[0]}")
"""
    sandbox.files.write("/home/user/test.py", script)

    # Execute it
    result = sandbox.commands.run("python3 /home/user/test.py")
    assert result.exit_code == 0
    assert "Python test successful" in result.stdout
    print(f"✓ Python executed:\n{result.stdout}")


if __name__ == "__main__":
    # Run with: uv run pytest tests/test_smoke.py -v -s
    pytest.main([__file__, "-v", "-s"])
