# Testing Guide

This document provides detailed information about running tests for the agent-sandboxes project.

## Quick Start

```bash
# Run all tests from root
./run_tests.sh

# Or test individual apps
cd apps/cli && uv run pytest tests/ -v
cd apps/mcp && uv run pytest tests/ -v
cd apps/obox && uv run pytest tests/ -v
```

## Prerequisites

### Required Environment Variables

Tests require valid API keys configured in `.env` files:

1. **Root `.env`** (for CLI and MCP tests):
   ```bash
   E2B_API_KEY=e2b_xxx...
   ```

2. **`working_dir/.env`** (for OBOX tests):
   ```bash
   E2B_API_KEY=e2b_xxx...
   CLAUDE_CODE_OAUTH_TOKEN=sk-ant-xxx...
   # OR
   ANTHROPIC_API_KEY=sk-ant-xxx...
   ```

3. **`working_dir/.mcp.json`** (for OBOX tests):
   ```json
   {
     "mcpServers": {
       "e2b-sandbox": {
         "command": "uv",
         "args": ["--directory", "../apps/mcp", "run", "server.py"],
         "env": {
           "E2B_API_KEY": "e2b_xxx..."
         }
       }
     }
   }
   ```

See [setup instructions](README.md#quick-start-with-obox) for details.

## Test Structure

### CLI Tests (`apps/cli/tests/`)

**File**: `test_smoke.py`

**What it tests**:
- ✅ Environment loading (E2B_API_KEY)
- ✅ Sandbox creation
- ✅ Command execution
- ✅ File write and read operations
- ✅ Directory operations (mkdir, exists, list, remove)
- ✅ Python script execution

**Run**:
```bash
cd apps/cli
uv sync
uv run pytest tests/ -v -s
```

**Expected output**:
```
test_env_loaded PASSED
test_sandbox_creation PASSED
test_command_execution PASSED
test_file_write_and_read PASSED
test_file_operations PASSED
test_python_execution PASSED
```

### MCP Tests (`apps/mcp/tests/`)

**File**: `test_smoke.py`

**What it tests**:
- ✅ Environment loading (E2B_API_KEY)
- ✅ MCP server module imports
- ✅ MCP tools registration (19 tools)
- ✅ Sandbox creation via E2B SDK
- ✅ CLI command execution via subprocess

**Run**:
```bash
cd apps/mcp
uv sync
uv run pytest tests/ -v -s
```

**Expected output**:
```
test_env_loaded PASSED
test_mcp_server_imports PASSED
test_mcp_tools_registered PASSED
test_init_sandbox_tool PASSED
test_cli_command_execution PASSED
```

### OBOX Tests (`apps/obox/tests/`)

**File**: `test_smoke.py`

**What it tests**:
- ✅ Environment loading from `working_dir/.env`
- ✅ Claude authentication (OAuth or API key)
- ✅ MCP config exists and is valid JSON
- ✅ Constants module (paths, tools, settings)
- ✅ Core modules import (agents, logs, hooks)
- ✅ Git utilities (URL validation, branch validation)
- ✅ Log directory structure
- ✅ System prompt exists with placeholders

**Run**:
```bash
cd apps/obox
uv sync
uv run pytest tests/ -v -s
```

**Expected output**:
```
test_working_dir_env_loaded PASSED
test_mcp_config_exists PASSED
test_constants_module PASSED
test_agents_module_imports PASSED
test_git_utils_validation PASSED
test_log_directory_structure PASSED
test_system_prompt_exists PASSED
```

## Test Philosophy

These are **smoke tests**, not comprehensive unit/integration tests:

- ✅ **Fast**: Run in seconds, not minutes
- ✅ **Simple**: No mocking, use real E2B sandboxes
- ✅ **Practical**: Verify actual functionality, not implementation details
- ✅ **Minimal setup**: Just need `.env` files configured
- ✅ **Clear output**: Print success messages with checkmarks

## Common Issues

### "E2B_API_KEY not found"

**Solution**: Copy `.env.example` to `.env` and add your E2B API key:
```bash
cp .env.example .env
# Edit .env and add: E2B_API_KEY=e2b_xxx...
```

### "MCP config not found"

**Solution**: Copy MCP config template and add your API key:
```bash
cp working_dir/.mcp.json.example working_dir/.mcp.json
# Edit working_dir/.mcp.json and replace "your-e2b-api-key-here"
```

### "CLAUDE_CODE_OAUTH_TOKEN not found"

**Solution**: Add Claude authentication to `working_dir/.env`:
```bash
# Option 1: Use OAuth token (recommended)
claude setup-token
# Copy the token to working_dir/.env

# Option 2: Use API key
# Add ANTHROPIC_API_KEY=sk-ant-xxx... to working_dir/.env
```

### Tests hang or timeout

**Cause**: Network issues or E2B API problems

**Solution**:
- Check your internet connection
- Verify E2B API key is valid
- Check E2B service status: https://e2b.dev/docs

## Test Fixtures

### Sandbox Fixture (CLI tests)

```python
@pytest.fixture
def sandbox():
    """Create a sandbox for testing, clean up after"""
    sbx = Sandbox.create(timeout=300)
    yield sbx
    sbx.kill()
```

This fixture:
- Creates a fresh E2B sandbox before each test
- Yields the sandbox to the test
- Automatically kills the sandbox after the test
- Handles cleanup even if test fails

## Adding New Tests

To add tests for a new module:

1. Create `tests/test_mymodule.py`
2. Import pytest and required modules
3. Write test functions starting with `test_`
4. Use fixtures for setup/teardown
5. Add assertions with clear error messages
6. Print success messages with ✓ checkmarks

Example:
```python
def test_my_feature(sandbox):
    """Test my new feature"""
    # Arrange
    expected = "result"

    # Act
    result = sandbox.commands.run("my-command")

    # Assert
    assert result.exit_code == 0
    assert expected in result.stdout
    print(f"✓ My feature works: {result.stdout}")
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install uv
        run: pip install uv
      - name: Run CLI tests
        env:
          E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
        run: |
          cd apps/cli
          uv sync
          uv run pytest tests/ -v
```

## Resources

- pytest documentation: https://docs.pytest.org/
- E2B SDK: https://e2b.dev/docs
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
