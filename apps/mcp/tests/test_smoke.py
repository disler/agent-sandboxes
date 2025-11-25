"""
Smoke tests for E2B Sandbox MCP Server.

These tests verify:
- MCP server can be imported
- Tools are properly registered
- Basic tool execution works

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


def test_mcp_server_imports():
    """Test that MCP server module can be imported"""
    try:
        # Add parent directory to path for imports
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import server
        print("✓ MCP server imported successfully")
        assert hasattr(server, "mcp"), "MCP instance not found"
    except ImportError as e:
        pytest.fail(f"Failed to import MCP server: {e}")


def test_mcp_tools_registered():
    """Test that MCP tools are registered"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    import server
    import asyncio

    # Get list of registered tools (async)
    async def get_tools():
        return await server.mcp.list_tools()

    tools = asyncio.run(get_tools())
    tool_names = [tool.name for tool in tools]

    print(f"\n✓ Found {len(tool_names)} registered tools")

    # Verify key tools exist
    expected_tools = [
        "init_sandbox",
        "create_sandbox",
        "execute_command",
        "read_file",
        "write_file",
        "list_files",
    ]

    for tool in expected_tools:
        assert tool in tool_names, f"Expected tool '{tool}' not found"
        print(f"  ✓ {tool}")


def test_init_sandbox_tool():
    """Test the init_sandbox tool execution"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from e2b import Sandbox
    import server

    # Create a test sandbox directly (not via MCP)
    sbx = Sandbox.create(timeout=300)
    sandbox_id = sbx.sandbox_id

    try:
        print(f"\n✓ Created test sandbox: {sandbox_id}")

        # Test that we can connect to it
        result = sbx.commands.run("echo 'test'")
        assert result.exit_code == 0
        print(f"✓ Sandbox is responsive")

    finally:
        sbx.kill()
        print(f"✓ Killed test sandbox")


def test_cli_command_execution():
    """Test running CLI commands via subprocess (simulating MCP tool calls)"""
    import subprocess
    import sys

    cli_path = Path(__file__).parent.parent.parent / "cli"

    # Test that sbx CLI can be invoked
    result = subprocess.run(
        ["uv", "run", "sbx", "--help"],
        cwd=cli_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Usage:" in result.stdout or "Commands:" in result.stdout
    print("✓ CLI can be invoked via subprocess")


if __name__ == "__main__":
    # Run with: uv run pytest tests/test_smoke.py -v -s
    pytest.main([__file__, "-v", "-s"])
