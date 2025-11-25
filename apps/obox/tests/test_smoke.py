"""
Smoke tests for OBOX (Orchestrated Sandbox).

These tests verify:
- Configuration is valid
- MCP config exists and is readable
- Constants are properly defined
- Core modules can be imported

Requirements:
- E2B_API_KEY must be set in working_dir/.env
- CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in working_dir/.env
- working_dir/.mcp.json must exist
"""

import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv


# Load .env from working_dir
working_dir = Path(__file__).parent.parent.parent.parent / "working_dir"
load_dotenv(working_dir / ".env")


def test_working_dir_env_loaded():
    """Verify required environment variables are loaded"""
    # E2B API key is required
    api_key = os.getenv("E2B_API_KEY")
    if api_key is None:
        pytest.skip("E2B_API_KEY not found in working_dir/.env - skipping (optional for config tests)")
    assert api_key.startswith("e2b_"), "E2B_API_KEY should start with 'e2b_'"
    print(f"✓ E2B_API_KEY loaded")

    # Claude auth (one of these must be set)
    claude_oauth = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not (claude_oauth or anthropic_key):
        pytest.skip("Claude authentication not found - skipping (optional for config tests)")
    print(f"✓ Claude authentication loaded")


def test_mcp_config_exists():
    """Verify MCP configuration file exists and is valid"""
    mcp_path = working_dir / ".mcp.json"
    assert mcp_path.exists(), f"MCP config not found at {mcp_path}"
    print(f"✓ MCP config exists: {mcp_path}")

    # Verify it's valid JSON
    with open(mcp_path, "r") as f:
        config = json.load(f)

    assert "mcpServers" in config, "MCP config missing 'mcpServers' key"
    assert "e2b-sandbox" in config["mcpServers"], "MCP config missing 'e2b-sandbox'"
    print(f"✓ MCP config is valid JSON with e2b-sandbox server")


def test_constants_module():
    """Test that constants module can be imported and has required values"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from modules.constants import (
        MCP_CONFIG_PATH,
        WORKING_DIR,
        LOG_DIR,
        ALLOWED_TOOLS,
        DEFAULT_MAX_TURNS,
    )

    # Verify paths
    assert WORKING_DIR.exists(), f"WORKING_DIR doesn't exist: {WORKING_DIR}"
    print(f"✓ WORKING_DIR exists: {WORKING_DIR}")

    assert MCP_CONFIG_PATH.exists(), f"MCP_CONFIG_PATH doesn't exist: {MCP_CONFIG_PATH}"
    print(f"✓ MCP_CONFIG_PATH exists: {MCP_CONFIG_PATH}")

    # Verify constants
    assert DEFAULT_MAX_TURNS > 0, "DEFAULT_MAX_TURNS must be positive"
    assert len(ALLOWED_TOOLS) > 0, "ALLOWED_TOOLS must not be empty"
    print(f"✓ Constants loaded: {len(ALLOWED_TOOLS)} allowed tools, max_turns={DEFAULT_MAX_TURNS}")


def test_agents_module_imports():
    """Test that agent module can be imported"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    try:
        from modules.agents import SandboxForkAgent
        from modules.logs import ForkLogger, LogManager
        from modules.hooks import create_hook_dict

        print("✓ All core modules imported successfully")
        print(f"  - SandboxForkAgent")
        print(f"  - ForkLogger, LogManager")
        print(f"  - create_hook_dict")
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_git_utils_validation():
    """Test git utility functions"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from modules.git_utils import validate_git_url, validate_branch_name

    # Test valid URLs
    assert validate_git_url("https://github.com/user/repo")
    assert validate_git_url("git@github.com:user/repo.git")
    print("✓ Git URL validation works")

    # Test valid branch names
    assert validate_branch_name("main")
    assert validate_branch_name("feature/new-api")
    assert validate_branch_name("fix-bug-123")
    print("✓ Git branch validation works")

    # Test invalid branch names
    assert not validate_branch_name("../etc/passwd")
    assert not validate_branch_name("branch with spaces")
    print("✓ Git validation rejects invalid inputs")


def test_log_directory_structure():
    """Test that log directory structure is correct"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from modules.constants import LOG_DIR, RUNTIME_DIR

    # Runtime dir should exist or be creatable
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    assert RUNTIME_DIR.exists(), f"RUNTIME_DIR doesn't exist: {RUNTIME_DIR}"
    print(f"✓ RUNTIME_DIR exists: {RUNTIME_DIR}")

    # Log dir should be creatable
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    assert LOG_DIR.exists(), f"LOG_DIR doesn't exist: {LOG_DIR}"
    print(f"✓ LOG_DIR exists: {LOG_DIR}")


def test_system_prompt_exists():
    """Test that system prompt file exists"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from modules.constants import SYSTEM_PROMPT_PATH

    assert SYSTEM_PROMPT_PATH.exists(), f"System prompt not found: {SYSTEM_PROMPT_PATH}"
    print(f"✓ System prompt exists: {SYSTEM_PROMPT_PATH}")

    # Verify it contains key placeholders
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        content = f.read()

    assert "{repo_url}" in content, "System prompt missing {repo_url} placeholder"
    assert "{branch}" in content, "System prompt missing {branch} placeholder"
    print("✓ System prompt has required placeholders")


if __name__ == "__main__":
    # Run with: uv run pytest tests/test_smoke.py -v -s
    pytest.main([__file__, "-v", "-s"])
