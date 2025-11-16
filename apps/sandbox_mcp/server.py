#!/usr/bin/env python3
"""
E2B Sandbox MCP Server

MCP server that wraps the E2B Sandbox CLI, providing tools for managing
sandboxes, executing commands, and manipulating files. All tools call the
underlying CLI via subprocess.

Usage:
    uv run mcp dev server.py
    uv run mcp install server.py
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "E2B Sandbox Manager",
    instructions="Manage E2B sandboxes for isolated code execution. Create sandboxes, execute commands, "
    "manage files, and control sandbox lifecycle. All operations are performed securely within isolated "
    "cloud environments.",
)

# Path to the CLI project (sibling directory)
CLI_PATH = Path(__file__).parent.parent / "sandbox_cli"


def run_sbx_cli(*args) -> dict:
    """
    Execute sbx CLI command and return parsed JSON or structured output.

    Args:
        *args: CLI arguments to pass to sbx command

    Returns:
        Parsed output from the CLI (dict or string)

    Raises:
        RuntimeError: If CLI command fails
    """
    cmd = ["uv", "run", "sbx", *args]

    # Create clean environment without VIRTUAL_ENV to avoid uv conflicts
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    try:
        result = subprocess.run(
            cmd,
            cwd=CLI_PATH,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        # Try to parse as JSON, otherwise return raw output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"output": result.stdout.strip(), "success": True}

    except subprocess.CalledProcessError as e:
        # Include both stdout and stderr for complete error context
        error_msg = f"CLI command failed with exit code {e.returncode}"
        if e.stdout and e.stdout.strip():
            error_msg += f"\nOutput: {e.stdout.strip()}"
        if e.stderr and e.stderr.strip():
            error_msg += f"\nError: {e.stderr.strip()}"
        raise RuntimeError(error_msg) from e


# ========================================
# Sandbox Initialization
# ========================================


@mcp.tool()
def init_sandbox(
    template: Optional[str] = None,
    timeout: int = 300,
    env_vars: Optional[str] = None,
) -> dict:
    """
    Initialize a new E2B sandbox and return the sandbox ID.

    Args:
        template: Sandbox template name (e.g., 'base')
        timeout: Sandbox timeout in seconds (default: 300)
        env_vars: Environment variables as comma-separated KEY=VALUE pairs

    Returns:
        Dict with sandbox_id and setup information
    """
    args = ["init", "--timeout", str(timeout)]

    if template:
        args.extend(["--template", template])

    if env_vars:
        for env_pair in env_vars.split(","):
            args.extend(["--env", env_pair.strip()])

    return run_sbx_cli(*args)


# ========================================
# Sandbox Lifecycle Management
# ========================================


@mcp.tool()
def create_sandbox(
    template: Optional[str] = None,
    timeout: int = 300,
    env_vars: Optional[str] = None,
    auto_pause: bool = False,
) -> dict:
    """
    Create a new sandbox with advanced options.

    Args:
        template: Sandbox template name
        timeout: Sandbox timeout in seconds
        env_vars: Environment variables as comma-separated KEY=VALUE pairs
        auto_pause: Enable auto-pause feature (beta)

    Returns:
        Dict with sandbox_id and configuration
    """
    args = ["sandbox", "create", "--timeout", str(timeout)]

    if template:
        args.extend(["--template", template])

    if env_vars:
        for env_pair in env_vars.split(","):
            args.extend(["--env", env_pair.strip()])

    if auto_pause:
        args.append("--auto-pause")

    return run_sbx_cli(*args)


@mcp.tool()
def connect_sandbox(sandbox_id: str, timeout: Optional[int] = None) -> dict:
    """
    Connect to an existing sandbox to verify it's running.

    Args:
        sandbox_id: The sandbox ID to connect to
        timeout: Optional connection timeout in seconds

    Returns:
        Connection status and sandbox information
    """
    args = ["sandbox", "connect", sandbox_id]
    if timeout:
        args.extend(["--timeout", str(timeout)])

    return run_sbx_cli(*args)


@mcp.tool()
def kill_sandbox(sandbox_id: str) -> dict:
    """
    Kill/terminate a sandbox.

    Args:
        sandbox_id: The sandbox ID to terminate

    Returns:
        Success confirmation
    """
    return run_sbx_cli("sandbox", "kill", sandbox_id)


@mcp.tool()
def get_sandbox_info(sandbox_id: str) -> dict:
    """
    Get detailed information about a sandbox.

    Args:
        sandbox_id: The sandbox ID

    Returns:
        Sandbox metadata including template, started time, etc.
    """
    return run_sbx_cli("sandbox", "info", sandbox_id)


@mcp.tool()
def check_sandbox_status(sandbox_id: str) -> dict:
    """
    Check if a sandbox is currently running.

    Args:
        sandbox_id: The sandbox ID

    Returns:
        Running status (true/false)
    """
    return run_sbx_cli("sandbox", "status", sandbox_id)


@mcp.tool()
def get_host(sandbox_id: str, port: int) -> dict:
    """
    Get the public hostname for an exposed port in the sandbox.

    Args:
        sandbox_id: The sandbox ID
        port: Port number to expose (e.g., 5173 for Vite, 3000 for Next.js)

    Returns:
        Public URL for the exposed port (e.g., https://xxxxx.e2b.app)
    """
    return run_sbx_cli("sandbox", "get-host", sandbox_id, "--port", str(port))


@mcp.tool()
def list_sandboxes(limit: int = 20) -> dict:
    """
    List all running sandboxes.

    Args:
        limit: Maximum number of sandboxes to return (default: 20)

    Returns:
        List of running sandboxes with their metadata
    """
    return run_sbx_cli("sandbox", "list", "--limit", str(limit))


@mcp.tool()
def pause_sandbox(sandbox_id: str) -> dict:
    """
    Pause a sandbox (beta feature).

    Args:
        sandbox_id: The sandbox ID

    Returns:
        Success confirmation
    """
    return run_sbx_cli("sandbox", "pause", sandbox_id)


# ========================================
# File Operations
# ========================================


@mcp.tool()
def list_files(sandbox_id: str, path: str = "/", depth: int = 1) -> dict:
    """
    List files and directories in a sandbox path.

    Args:
        sandbox_id: The sandbox ID
        path: Directory path to list (default: "/")
        depth: Directory depth to traverse (default: 1)

    Returns:
        List of files with metadata (name, type, size, permissions)
    """
    return run_sbx_cli("files", "ls", sandbox_id, path, "--depth", str(depth))


@mcp.tool()
def read_file(sandbox_id: str, path: str) -> dict:
    """
    Read a text file from the sandbox.

    Args:
        sandbox_id: The sandbox ID
        path: File path to read

    Returns:
        File content as string
    """
    return run_sbx_cli("files", "read", sandbox_id, path)


@mcp.tool()
def write_file(sandbox_id: str, path: str, content: str) -> dict:
    """
    Write text content to a file in the sandbox.

    Args:
        sandbox_id: The sandbox ID
        path: File path to write to
        content: Text content to write

    Returns:
        Success confirmation with file path
    """
    return run_sbx_cli("files", "write", sandbox_id, path, content)


@mcp.tool()
def upload_file(sandbox_id: str, local_path: str, remote_path: str) -> dict:
    """
    Upload a binary file to the sandbox.

    Args:
        sandbox_id: The sandbox ID
        local_path: Path to local file to upload
        remote_path: Destination path in sandbox

    Returns:
        Success confirmation with file size
    """
    return run_sbx_cli("files", "upload", sandbox_id, local_path, remote_path)


@mcp.tool()
def download_file(sandbox_id: str, remote_path: str, local_path: str) -> dict:
    """
    Download a file from the sandbox.

    Args:
        sandbox_id: The sandbox ID
        remote_path: Path to file in sandbox
        local_path: Local destination path

    Returns:
        Success confirmation with file size
    """
    return run_sbx_cli("files", "download", sandbox_id, remote_path, local_path)


@mcp.tool()
def check_file_exists(sandbox_id: str, path: str) -> dict:
    """
    Check if a file or directory exists.

    Args:
        sandbox_id: The sandbox ID
        path: Path to check

    Returns:
        Existence status (true/false)
    """
    return run_sbx_cli("files", "exists", sandbox_id, path)


@mcp.tool()
def get_file_info(sandbox_id: str, path: str) -> dict:
    """
    Get detailed information about a file.

    Args:
        sandbox_id: The sandbox ID
        path: File path

    Returns:
        File metadata (name, size, type, permissions)
    """
    return run_sbx_cli("files", "info", sandbox_id, path)


@mcp.tool()
def remove_file(sandbox_id: str, path: str) -> dict:
    """
    Remove a file or directory.

    Args:
        sandbox_id: The sandbox ID
        path: Path to remove

    Returns:
        Success confirmation
    """
    return run_sbx_cli("files", "rm", sandbox_id, path)


@mcp.tool()
def make_directory(sandbox_id: str, path: str) -> dict:
    """
    Create a directory in the sandbox.

    Args:
        sandbox_id: The sandbox ID
        path: Directory path to create

    Returns:
        Success confirmation
    """
    return run_sbx_cli("files", "mkdir", sandbox_id, path)


@mcp.tool()
def rename_file(sandbox_id: str, old_path: str, new_path: str) -> dict:
    """
    Rename or move a file/directory.

    Args:
        sandbox_id: The sandbox ID
        old_path: Current path
        new_path: New path

    Returns:
        Success confirmation with new path
    """
    return run_sbx_cli("files", "mv", sandbox_id, old_path, new_path)


# ========================================
# Command Execution
# ========================================


@mcp.tool()
def execute_command(
    sandbox_id: str,
    command: str,
    cwd: Optional[str] = None,
    user: Optional[str] = None,
    root: bool = False,
    shell: bool = False,
    env_vars: Optional[str] = None,
    timeout: int = 60,
    background: bool = False,
) -> dict:
    """
    Execute a command in the sandbox with full control.

    Args:
        sandbox_id: The sandbox ID
        command: Command to execute
        cwd: Working directory for command execution
        user: Run as specific user
        root: Run as root user (shortcut)
        shell: Execute in shell context (enables pipes, redirections)
        env_vars: Environment variables as comma-separated KEY=VALUE pairs
        timeout: Command timeout in seconds (0 for unlimited)
        background: Run command in background

    Returns:
        Command output with stdout, stderr, and exit code
    """
    args = ["exec", sandbox_id, command]

    if cwd:
        args.extend(["--cwd", cwd])

    if user:
        args.extend(["--user", user])

    if root:
        args.append("--root")

    if shell:
        args.append("--shell")

    if env_vars:
        for env_pair in env_vars.split(","):
            args.extend(["--env", env_pair.strip()])

    args.extend(["--timeout", str(timeout)])

    if background:
        args.append("--background")

    return run_sbx_cli(*args)


if __name__ == "__main__":
    mcp.run()
