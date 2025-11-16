# E2B Sandbox MCP Server

Model Context Protocol (MCP) server that provides LLMs with access to E2B sandbox environments through structured tool calls.

## Overview

This MCP server wraps the E2B Sandbox CLI (located in `../sandbox_cli/`) and exposes each CLI command as an MCP tool. It provides one-to-one mappings, allowing LLMs to:

- Create and manage isolated sandbox environments
- Execute commands with full control (shell, root, environment variables)
- Perform file operations (read, write, upload, download)
- Manage sandbox lifecycle (create, connect, kill, pause)
- All operations performed securely within E2B cloud sandboxes

## Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Claude / LLM Client                            │
│                                                 │
└───────────────────┬─────────────────────────────┘
                    │ MCP Protocol
                    │
┌───────────────────▼─────────────────────────────┐
│                                                 │
│  E2B Sandbox MCP Server (this app)              │
│  • 19 MCP Tools                                 │
│  • FastMCP Framework                            │
│                                                 │
└───────────────────┬─────────────────────────────┘
                    │ subprocess calls
                    │
┌───────────────────▼─────────────────────────────┐
│                                                 │
│  E2B Sandbox CLI (apps/sandbox_cli/)            │
│  • Sandbox management                           │
│  • File operations with SDK APIs                │
│  • Command execution                            │
│                                                 │
└───────────────────┬─────────────────────────────┘
                    │ E2B SDK
                    │
┌───────────────────▼─────────────────────────────┐
│                                                 │
│  E2B Cloud Sandboxes                            │
│  Isolated code execution environments           │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Installation

```bash
# Navigate to this directory
cd apps/sandbox_mcp

# Install dependencies
uv sync
```

## Quick Start

### Test with MCP Inspector

```bash
# Test the server interactively
uv run mcp dev server.py
```

This opens the MCP Inspector where you can:
- Browse available tools
- Test tool calls with different parameters
- See structured responses

### Install in Claude Desktop

```bash
# Install for use with Claude Desktop
uv run mcp install server.py

# Or with custom name
uv run mcp install server.py --name "E2B Sandboxes"
```

## Available Tools

The server exposes 19 tools, each mapping to an E2B Sandbox CLI command:

### Sandbox Initialization

- **init_sandbox** - Quick sandbox initialization with template support

### Sandbox Lifecycle Management

- **create_sandbox** - Create a new sandbox with advanced options
- **connect_sandbox** - Connect to an existing sandbox
- **kill_sandbox** - Terminate a sandbox
- **get_sandbox_info** - Get detailed sandbox metadata
- **check_sandbox_status** - Check if sandbox is running
- **pause_sandbox** - Pause a sandbox (beta feature)

### File Operations

- **list_files** - List files and directories
- **read_file** - Read text file content
- **write_file** - Write text content to a file
- **upload_file** - Upload binary files (images, PDFs, executables, etc.)
- **download_file** - Download files from sandbox
- **check_file_exists** - Check if a file exists
- **get_file_info** - Get file metadata (size, permissions, type)
- **remove_file** - Remove files or directories
- **make_directory** - Create directories
- **rename_file** - Rename or move files/directories

### Command Execution

- **execute_command** - Execute commands with full control (shell, root, env vars, cwd, timeout, background)

## Example Usage

Once installed in Claude Desktop, you can ask:

```
"Create a new E2B sandbox with Python environment"
→ Calls init_sandbox(template="base")

"List files in /home/user directory"
→ Calls list_files(sandbox_id="...", path="/home/user")

"Install numpy and run a Python script"
→ Calls execute_command(sandbox_id="...", command="pip install numpy")
→ Calls execute_command(sandbox_id="...", command="python script.py")

"Upload my image.png to the sandbox"
→ Calls upload_file(sandbox_id="...", local_path="./image.png", remote_path="/home/user/image.png")

"Execute a command as root"
→ Calls execute_command(sandbox_id="...", command="apt-get update", root=True)

"Run a shell command with pipes"
→ Calls execute_command(sandbox_id="...", command="ps aux | grep python", shell=True)
```

## Implementation Details

### Tool Design

Each tool:
1. Accepts the same parameters as the corresponding CLI command
2. Builds and executes `uv run sbx <command> [args]` via subprocess
3. Returns parsed output as structured data (JSON when available)
4. Handles errors gracefully with descriptive messages

### No Direct API Calls

The MCP server intentionally **does not** make direct calls to E2B SDK. Instead:
- ✅ Delegates all sandbox logic to the battle-tested CLI
- ✅ Single source of truth for sandbox interaction
- ✅ Easier maintenance (updates only in CLI)
- ✅ Consistent behavior between CLI and MCP usage

### Output Handling

The server intelligently handles both JSON and text output:
- JSON output is parsed and returned as structured data
- Text output is wrapped in `{"output": "...", "success": true}`
- Errors are caught and raised as RuntimeError with stderr details

## Development

### Project Structure

```
apps/sandbox_mcp/
├── server.py           # Main MCP server implementation
├── pyproject.toml      # Project dependencies and metadata
└── README.md           # This file
```

### Running Locally

```bash
# Run with stdio transport (default)
uv run python server.py

# Or use mcp dev for interactive testing
uv run mcp dev server.py
```

### Adding New Tools

To add a new tool when the CLI adds a command:

1. Add the CLI command to `../sandbox_cli/`
2. In `server.py`, add a new `@mcp.tool()` decorated function
3. Call `run_sbx_cli()` with appropriate arguments
4. Document parameters and return value

## API Documentation

All tools use the E2B SDK under the hood:
- SDK Docs: https://e2b.dev/docs
- Python SDK: https://github.com/e2b-dev/e2b
- No authentication required - uses E2B_API_KEY from environment

## Use Cases

### Code Execution Environment
```
"Create a Python sandbox and run my analysis script"
```

### File Processing
```
"Upload these CSV files and process them with pandas"
```

### Development Environment
```
"Set up a Node.js project with dependencies and run tests"
```

### Data Science Workflow
```
"Create a sandbox, install scikit-learn, train a model, and download the results"
```

### System Administration
```
"Install nginx, configure it, and check if it's running"
```

## Security

- All operations run in isolated E2B cloud sandboxes
- Sandboxes are ephemeral and can be terminated at any time
- Root access available when needed but sandboxed
- File uploads/downloads go through E2B SDK securely

## License

MIT
