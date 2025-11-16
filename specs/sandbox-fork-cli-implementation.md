# Plan: Sandbox Fork CLI - Multi-Agent Git Repository Workflow

## Task Description
Build a Typer CLI command `sandbox-fork` that clones a git repository into multiple E2B sandboxes (forks), runs isolated Claude Code agents in each sandbox with a given prompt, and streams the execution results to separate log files. The tool enables parallel experimentation on codebases where each fork operates independently with full sandbox isolation.

## Objective
Create a production-ready CLI tool that:
1. Accepts a git repository URL, optional branch, prompt (text or file), and fork count
2. Initializes N isolated E2B sandboxes with MCP server access
3. Clones the repository into each sandbox
4. Runs a Claude Code agent in each sandbox that executes the given prompt
5. Streams all agent activity to dedicated log files per fork
6. Opens log files in VSCode for real-time monitoring
7. Returns summary of branch names and log file paths

## Problem Statement
Developers and AI researchers need to run parallel experiments on codebases where each experiment requires:
- Complete isolation (no cross-contamination between forks)
- Full environment control (install packages, modify files, run commands)
- Sandboxed execution (agents cannot access local filesystem)
- Real-time logging for monitoring progress
- Multi-threading for performance

Current solutions don't provide this level of isolation + parallel execution + agent orchestration in a single command.

## Solution Approach

### Architecture Overview
```
┌─────────────────────────────────────────────────────┐
│  CLI Entry Point (obox sandbox-fork)                │
│  - Parse arguments (repo, branch, prompt, forks)    │
│  - Validate inputs                                   │
│  - Generate branch names if not provided            │
└────────────────┬────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────┐
│  Fork Orchestrator (agents.py)                      │
│  - Create N threads (one per fork)                  │
│  - Initialize log files for each fork               │
│  - Launch parallel agent executions                 │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        v                 v
┌──────────────┐  ┌──────────────┐
│  Fork 1      │  │  Fork N      │
│  Thread      │  │  Thread      │
└──────┬───────┘  └──────┬───────┘
       │                 │
       v                 v
┌──────────────┐  ┌──────────────┐
│ E2B Sandbox  │  │ E2B Sandbox  │
│ + MCP Server │  │ + MCP Server │
└──────┬───────┘  └──────┬───────┘
       │                 │
       v                 v
┌──────────────┐  ┌──────────────┐
│ Claude Agent │  │ Claude Agent │
│ - Clone repo │  │ - Clone repo │
│ - Run prompt │  │ - Run prompt │
│ - Stream logs│  │ - Stream logs│
└──────────────┘  └──────────────┘
```

### Key Design Decisions

1. **Sandbox Isolation**: Each fork gets its own E2B sandbox with isolated filesystem, preventing cross-fork interference

2. **MCP Server Architecture**: Agents use MCP tools (not local tools) to ensure all operations happen in sandboxes:
   - `init_sandbox` - Create sandbox
   - `execute_command` - Clone repo, run git commands
   - `write_file` - Create files in sandbox
   - `read_file` - Read files from sandbox
   - Local tools (Read, Write, Edit, Bash, etc.) are DISALLOWED

3. **Multi-threading**: Python threading for parallel execution with thread-safe log writing

4. **Logging Strategy**: Each fork writes to `logs/fork-{N}-{timestamp}.log` with structured format for easy parsing

5. **Working Directory**: `apps/sandbox_agent_working_dir/temp/` is the ONLY local directory for temporary files

6. **Agent System Prompt**: Custom prompt that enforces sandbox-only operations and explains available MCP tools

## Required Reading

**IMPORTANT:** Before implementing, thoroughly read these files to understand the architecture. The implementation depends heavily on hooks, MCP tools, and agent patterns.

### 1. Claude Agent SDK Documentation (READ FIRST)
**File:** `ai_docs/claude-agent-sdk-python.md`

**Critical sections:**
- **Hooks (Lines 919-1029)** - ALL 6 hook types and their signatures
  - `PreToolUse` - How to validate/block tool calls before execution
  - `PostToolUse` - How to log tool results after execution
  - `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact` - Lifecycle hooks
  - Hook callback signatures: `async def(input_data, tool_use_id, context) -> dict`
  - Hook response format for blocking: `{"hookSpecificOutput": {"permissionDecision": "deny", ...}}`
- **ClaudeSDKClient (Lines 217-254)** - Session management, `receive_response()` loop
- **ClaudeAgentOptions (Lines 449-510)** - Configuration: tools, hooks, MCP servers, system prompts
- **HookMatcher (Lines 968-977)** - How to register hooks with matchers
- **Hook examples (Lines 982-1040)** - Real-world hook implementations

**What you'll learn:**
- How to create async hook functions that log and validate tool usage
- How to block tool execution by returning specific hook response format
- How to extract data from `input_data` dict (tool_name, tool_input, result, is_error)
- How to integrate hooks into `ClaudeAgentOptions` with `HookMatcher`

### 2. Custom Agent Pattern (READ SECOND)
**File:** `ai_docs/agent_manager_custom_agents_example.md`

**Critical sections:**
- **Hook factories (Lines 1451-1530)** - `create_pre_tool_hook()` pattern
- **Hook implementation (Lines 1532-1612)** - `create_post_tool_hook()` pattern
- **Hook dictionary (Lines 939-1011)** - Building complete hooks with `HookMatcher`
- **Agent options (Lines 709-731, 842-854)** - Full `ClaudeAgentOptions` configuration
- **Message processing (Lines 1013-1326)** - `receive_response()` loop with all message types

**What you'll learn:**
- Factory function pattern for creating hooks with closures (captures logger)
- How to build hooks dictionary with ALL hook types registered
- How to process `AssistantMessage`, `TextBlock`, `ToolUseBlock`, `ResultMessage`
- How to extract cost and token data from `ResultMessage.usage`
- Threading pattern for parallel agent execution

### 3. MCP Server Implementation
**File:** `apps/sandbox_mcp/server.py`

**Critical sections:**
- **execute_command tool (Lines 379-431)** - MOST IMPORTANT tool signature
  - Parameters: `command`, `cwd`, `user`, `root`, `shell`, `env_vars`, `timeout`, `background`
  - How to pass arguments to E2B CLI via subprocess
- **File operation tools (Lines 219-370)** - All file tools available
- **Sandbox lifecycle tools (Lines 71-212)** - init, create, connect, kill, pause

**What you'll learn:**
- Tool naming: `mcp__e2b__<tool_name>`
- How tools are wrapped around E2B SDK
- What parameters each tool accepts
- How tools return structured JSON responses

### 4. E2B SDK Reference
**Files:** `ai_docs/e2b-python-sdk-sandbox-sync.md`, `ai_docs/sandbox-async.md`

**Key concepts to understand:**
- Sandbox isolation model and security
- File operations: `read()`, `write()`, `list()`, `exists()`
- Command execution: `run()` with `background`, `cwd`, `env`, parameters
- Sandbox lifecycle: `create()`, `connect()`, `kill()`

**Note:** We use MCP tools (not direct SDK), but understanding the SDK helps you know what's possible.

### 5. Existing CLI Implementation
**File:** `apps/sandbox_cli/README.md` and `apps/sandbox_cli/src/`

**What to learn:**
- Typer CLI structure and command registration
- Rich console formatting patterns
- Error handling and validation patterns
- Project organization: `src/main.py`, `src/commands/`, `src/modules/`

**Examine:**
- `src/main.py` - How to create Typer app and register commands
- `src/commands/*.py` - Command implementation patterns
- `src/modules/*.py` - Utility module organization

### 6. Working Directory Structure
**Path:** `apps/sandbox_agent_working_dir/`

**Understand:**
- `logs/` - Where fork logs are written (OUTSIDE temp/)
- `temp/` - Local file operations directory (path restrictions enforced)
- `.mcp.json` - MCP server configuration (referenced by agents)

## Relevant Files

### Existing Files (Reference)
- `ai_docs/claude-agent-sdk-python.md` - **READ FIRST** - Hook patterns and agent SDK
- `ai_docs/agent_manager_custom_agents_example.md` - **READ SECOND** - Real implementation
- `apps/sandbox_mcp/server.py` - MCP server and available tools
- `ai_docs/e2b-python-sdk-sandbox-sync.md` - E2B SDK reference
- `ai_docs/sandbox-async.md` - Async patterns
- `apps/sandbox_cli/` - Existing CLI for patterns
- `apps/sandbox_agent_working_dir/` - Working directory structure

### New Files

#### `apps/sandbox_workflows/pyproject.toml`
- UV project configuration
- Dependencies: typer, rich, claude-agent-sdk, python-dotenv
- CLI entry point: `obox = "src.main:app"`

#### `apps/sandbox_workflows/src/main.py`
- Typer app initialization
- CLI entry point
- Imports and registers all commands

#### `apps/sandbox_workflows/src/commands/__init__.py`
- Command module initialization
- Exports all command functions

#### `apps/sandbox_workflows/src/commands/sandbox_fork.py`
- Main CLI command implementation
- Argument parsing and validation
- Orchestrates fork creation and execution
- Opens VSCode with log files

#### `apps/sandbox_workflows/src/modules/__init__.py`
- Module initialization
- Exports all utility modules

#### `apps/sandbox_workflows/src/modules/constants.py`
- Configuration constants
- Default values (fork count, timeouts, etc.)
- MCP server configuration paths
- Logging configuration
- Tool allow/deny lists

#### `apps/sandbox_workflows/src/modules/logs.py`
- Log file creation and management
- Thread-safe log writing
- Structured log formatting
- Log file path generation

#### `apps/sandbox_workflows/src/modules/hooks.py`
- **NEW**: Hook implementations for tool observability and path gating
- PreToolUse hook: Log tool calls and validate paths
- PostToolUse hook: Log tool results and track file operations
- Path validation: Restrict Read/Write/Edit to temp/ directory only
- Full observability: Track all tool usage in logs

#### `apps/sandbox_workflows/src/modules/agents.py`
- Claude Code agent creation and configuration
- MCP server integration
- Hook setup and registration
- Agent execution in threads
- Message streaming and logging

#### `apps/sandbox_workflows/src/modules/git_utils.py`
- Git repository validation
- Branch name generation (if not provided)
- Repository URL parsing

#### `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_system_prompt.md`
- Custom system prompt for agents
- Explains hybrid operation model (sandbox + local temp/)
- Lists available tools (MCP + local)
- Defines temp/ directory restriction for local file operations

#### `apps/sandbox_workflows/.env.sample`
- Environment variable template
- ANTHROPIC_API_KEY placeholder
- E2B_API_KEY placeholder

#### `apps/sandbox_workflows/README.md`
- Project documentation
- Usage examples
- Architecture overview

## Implementation Phases

### Phase 1: Foundation (Project Setup)
- Initialize UV project in `apps/sandbox_workflows/`
- Set up project structure (src/, commands/, modules/, prompts/)
- Create pyproject.toml with dependencies
- Set up environment configuration

### Phase 2: Core Implementation (Modules)
- Implement constants.py with configuration
- Build logs.py for thread-safe log management
- Create git_utils.py for repository operations
- Write system prompt in prompts/
- Implement agents.py with Claude SDK integration

### Phase 3: CLI & Integration (Command)
- Build sandbox_fork.py CLI command
- Integrate all modules
- Add multi-threading for parallel forks
- Implement VSCode integration for log viewing
- Add error handling and validation

## Step by Step Tasks

### 1. Initialize UV Project Structure
- Navigate to `apps/sandbox_workflows/`
- Run `uv init` to create new project
- Create directory structure: `src/`, `src/commands/`, `src/modules/`, `src/prompts/`
- Initialize `__init__.py` files in all Python directories

### 2. Create pyproject.toml Configuration
- Define project metadata (name: "obox", version: "0.1.0")
- Add dependencies:
  - `typer[all]>=0.9.0` - CLI framework
  - `rich>=13.0.0` - Terminal formatting
  - `claude-agent-sdk>=0.1.0` - Claude Code agent SDK
  - `python-dotenv>=1.0.0` - Environment variables
  - `e2b>=2.6.4` - E2B sandbox SDK (if needed for types)
- Configure CLI entry point: `[project.scripts]` with `obox = "src.main:app"`
- Set Python requirement: `requires-python = ">=3.12"`

### 3. Implement constants.py (Configuration)
```python
# src/modules/constants.py

"""
Configuration constants for sandbox-fork CLI.
"""

from pathlib import Path
from typing import Final

# === Project Paths ===
# Root directory of the sandbox_workflows project
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent

# Working directory for agent execution (base directory)
WORKING_DIR: Final[Path] = PROJECT_ROOT.parent / "sandbox_agent_working_dir"

# Temp directory for local file operations (hooks enforce this restriction)
TEMP_DIR: Final[Path] = WORKING_DIR / "temp"

# Log directory for fork execution logs (separate from temp/)
LOG_DIR: Final[Path] = WORKING_DIR / "logs"

# MCP server configuration path (relative to agent-sandboxes root)
MCP_CONFIG_PATH: Final[Path] = WORKING_DIR / ".mcp.json"

# System prompt file path
SYSTEM_PROMPT_PATH: Final[Path] = PROJECT_ROOT / "src" / "prompts" / "sandbox_fork_agent_system_prompt.md"

# === Default Values ===
# Default number of forks to create
DEFAULT_FORKS: Final[int] = 1

# Maximum number of forks allowed
MAX_FORKS: Final[int] = 100

# Default sandbox timeout in seconds (5 minutes)
DEFAULT_SANDBOX_TIMEOUT: Final[int] = 300

# Default agent max turns
DEFAULT_MAX_TURNS: Final[int] = 100

# Default sandbox template
DEFAULT_TEMPLATE: Final[str] = "base"

# === Tools Configuration ===
# Allowed tools (MCP + local with hook-based restrictions)
ALLOWED_TOOLS: Final[list[str]] = [
    # MCP E2B Sandbox Tools (operate in isolated sandbox)
    "mcp__e2b__init_sandbox",
    "mcp__e2b__execute_command",
    "mcp__e2b__write_file",
    "mcp__e2b__read_file",
    "mcp__e2b__list_files",
    "mcp__e2b__upload_file",
    "mcp__e2b__download_file",
    "mcp__e2b__make_directory",
    "mcp__e2b__remove_file",
    "mcp__e2b__rename_file",
    "mcp__e2b__check_file_exists",
    "mcp__e2b__get_file_info",
    "mcp__e2b__kill_sandbox",
    # Local Tools (restricted by hooks to TEMP_DIR only)
    "Read",      # Hook validates path is within TEMP_DIR
    "Write",     # Hook validates path is within TEMP_DIR
    "Edit",      # Hook validates path is within TEMP_DIR
    "Bash",      # Hook logs all commands for observability
    # Utility Tools
    "WebFetch",
    "WebSearch",
    "Task",
    "Skill",
    "SlashCommand",
]

# Disallowed tools (not needed for this workflow)
DISALLOWED_TOOLS: Final[list[str]] = [
    "Glob",          # Use mcp__e2b__list_files instead
    "Grep",          # Use mcp__e2b__read_file + processing instead
    "NotebookEdit",  # Not needed for git workflows
    "TodoWrite",     # Not needed for automated workflows
]

# === Path Restriction Configuration ===
# Tools that require path validation (must operate within TEMP_DIR)
PATH_RESTRICTED_TOOLS: Final[set[str]] = {
    "Read",
    "Write",
    "Edit",
}

# Temp directory name for path validation
TEMP_DIR_NAME: Final[str] = "temp"

# === Logging Configuration ===
# Log file name template
LOG_FILE_TEMPLATE: Final[str] = "fork-{fork_num}-{timestamp}.log"

# Log timestamp format
LOG_TIMESTAMP_FORMAT: Final[str] = "%Y%m%d-%H%M%S"

# === Git Configuration ===
# Default branch name template if not provided
DEFAULT_BRANCH_TEMPLATE: Final[str] = "fork-experiment-{timestamp}"
```

### 4. Implement logs.py (Log Management)
```python
# src/modules/logs.py

"""
Thread-safe logging utilities for fork execution.
"""

import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from .constants import LOG_DIR, LOG_FILE_TEMPLATE, LOG_TIMESTAMP_FORMAT


class ForkLogger:
    """
    Thread-safe logger for individual fork execution.

    Manages log file creation, writing, and formatting for a single fork.
    """

    def __init__(self, fork_num: int, repo_name: str):
        """
        Initialize fork logger.

        Args:
            fork_num: Fork number (1-indexed)
            repo_name: Repository name for context
        """
        # Generate timestamp for log file name
        # Create log file path using template
        # Initialize thread lock for safe writing
        # Create log directory if it doesn't exist
        # Open log file in write mode
        # Write header with fork info
        pass

    def log(self, level: str, message: str, **kwargs):
        """
        Write a log entry with timestamp and level.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            **kwargs: Additional key-value pairs to log
        """
        # Acquire thread lock
        # Format timestamp
        # Format message with level and timestamp
        # Add kwargs if present
        # Write to log file
        # Flush buffer
        # Release lock
        pass

    def log_agent_message(self, message_type: str, content: str):
        """
        Log agent message in structured format.

        Args:
            message_type: Type of message (TextBlock, ToolUseBlock, etc.)
            content: Message content
        """
        # Format as structured log entry
        # Call self.log() with formatted data
        pass

    def log_error(self, error: Exception):
        """
        Log error with full traceback.

        Args:
            error: Exception to log
        """
        # Format exception with traceback
        # Log as ERROR level
        pass

    def close(self):
        """Close log file and release resources."""
        # Write footer
        # Close file handle
        pass

    @property
    def log_path(self) -> Path:
        """Get path to log file."""
        # Return path to log file
        pass


class LogManager:
    """
    Manager for creating and tracking multiple fork loggers.
    """

    def __init__(self, repo_name: str):
        """
        Initialize log manager.

        Args:
            repo_name: Repository name for context
        """
        # Store repo name
        # Initialize dict to track loggers by fork number
        # Ensure log directory exists
        pass

    def create_logger(self, fork_num: int) -> ForkLogger:
        """
        Create logger for a fork.

        Args:
            fork_num: Fork number

        Returns:
            ForkLogger instance
        """
        # Create ForkLogger instance
        # Store in tracking dict
        # Return logger
        pass

    def get_logger(self, fork_num: int) -> Optional[ForkLogger]:
        """Get logger for fork number."""
        # Return logger from tracking dict
        pass

    def get_all_log_paths(self) -> list[Path]:
        """Get paths to all log files."""
        # Collect log_path from all loggers
        # Return as list
        pass

    def close_all(self):
        """Close all loggers."""
        # Iterate over all loggers
        # Call close() on each
        pass
```

### 5. Implement hooks.py (Hook-Based Observability & Path Gating)
```python
# src/modules/hooks.py

"""
Hook implementations for tool observability and path restrictions.

Hooks provide:
1. Full observability - Log ALL tool usage to fork logs
2. Path gating - Restrict Read/Write/Edit to temp/ directory only
3. Security - Prevent accidental local filesystem access outside temp/
"""

from pathlib import Path
from typing import Any, Dict, Optional
from .constants import PATH_RESTRICTED_TOOLS, TEMP_DIR, TEMP_DIR_NAME
from .logs import ForkLogger


def create_pre_tool_hook(logger: ForkLogger):
    """
    Create PreToolUse hook for logging and path validation.

    This hook runs BEFORE any tool is executed.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def pre_tool_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PreToolUse hook implementation.

        Logs tool usage and validates file paths for restricted tools.

        Args:
            input_data: Dict with 'tool_name' and 'tool_input'
            tool_use_id: Tool use ID from Claude
            context: Hook context

        Returns:
            Hook response dict (may contain 'decision': 'block' to deny)
        """
        # Extract tool name and input
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Log the tool usage
        logger.log(
            "INFO",
            f"[PreToolUse] {tool_name}",
            tool_use_id=tool_use_id,
            tool_input=str(tool_input)[:200]  # Truncate for readability
        )

        # === PATH VALIDATION FOR RESTRICTED TOOLS ===
        if tool_name in PATH_RESTRICTED_TOOLS:
            # Extract file_path from tool input
            file_path_str = tool_input.get("file_path")

            if not file_path_str:
                # No file_path provided - shouldn't happen but allow
                logger.log("WARNING", f"{tool_name} called without file_path")
                return {}

            # Convert to Path and resolve to absolute path
            file_path = Path(file_path_str).resolve()

            # Check if path is within TEMP_DIR
            try:
                # Check if file_path is relative to TEMP_DIR
                file_path.relative_to(TEMP_DIR)
                # Path is within TEMP_DIR - allow
                logger.log(
                    "DEBUG",
                    f"[PathValidation] {tool_name} path OK: {file_path_str}"
                )
                return {}  # Allow

            except ValueError:
                # Path is OUTSIDE TEMP_DIR - BLOCK
                logger.log(
                    "ERROR",
                    f"[PathValidation] BLOCKED {tool_name} - path outside temp/: {file_path_str}",
                    reason="Path must be within temp/ directory"
                )

                # Return block decision
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"Path '{file_path_str}' is outside the allowed temp/ directory. "
                            f"All local file operations must be within temp/. "
                            f"Use MCP sandbox tools (mcp__e2b__*) for sandbox operations."
                        )
                    }
                }

        # === BASH COMMAND LOGGING ===
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            logger.log(
                "INFO",
                f"[Bash] Executing local command",
                command=command[:100]  # Truncate long commands
            )

        # === MCP TOOL LOGGING ===
        elif tool_name.startswith("mcp__e2b__"):
            # Log MCP sandbox operations
            logger.log(
                "INFO",
                f"[SandboxOp] {tool_name}",
                sandbox_operation=tool_name.replace("mcp__e2b__", "")
            )

        # Allow tool execution
        return {}

    return pre_tool_hook


def create_post_tool_hook(logger: ForkLogger):
    """
    Create PostToolUse hook for logging tool results.

    This hook runs AFTER any tool is executed.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def post_tool_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PostToolUse hook implementation.

        Logs tool results and any errors.

        Args:
            input_data: Dict with 'tool_name', 'result', 'is_error'
            tool_use_id: Tool use ID
            context: Hook context

        Returns:
            Empty dict (PostToolUse cannot block)
        """
        # Extract tool info
        tool_name = input_data.get("tool_name", "unknown")
        result = input_data.get("result")
        is_error = input_data.get("is_error", False)

        # Log based on success/failure
        if is_error:
            logger.log(
                "ERROR",
                f"[PostToolUse] {tool_name} FAILED",
                tool_use_id=tool_use_id,
                error=str(result)[:200]
            )
        else:
            # Truncate large results for logging
            result_preview = str(result)[:150] if result else "No result"
            logger.log(
                "INFO",
                f"[PostToolUse] {tool_name} completed",
                tool_use_id=tool_use_id,
                result_preview=result_preview
            )

        # === FILE TRACKING (Optional Enhancement) ===
        # Track which files were modified/read
        if tool_name in {"Write", "Edit"}:
            file_path = input_data.get("tool_input", {}).get("file_path")
            if file_path:
                logger.log(
                    "DEBUG",
                    f"[FileTracking] Modified: {file_path}"
                )
        elif tool_name == "Read":
            file_path = input_data.get("tool_input", {}).get("file_path")
            if file_path:
                logger.log(
                    "DEBUG",
                    f"[FileTracking] Read: {file_path}"
                )

        return {}

    return post_tool_hook


def create_user_prompt_hook(logger: ForkLogger):
    """
    Create UserPromptSubmit hook for logging user prompts.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def user_prompt_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        UserPromptSubmit hook - logs when user submits a prompt.

        Args:
            input_data: Dict with 'prompt'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict (cannot modify prompt)
        """
        prompt = input_data.get("prompt", "")
        logger.log(
            "INFO",
            "[UserPromptSubmit] Agent received prompt",
            prompt_length=len(prompt),
            prompt_preview=prompt[:200]  # Log first 200 chars
        )
        return {}

    return user_prompt_hook


def create_stop_hook(logger: ForkLogger):
    """
    Create Stop hook for logging agent session end.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def stop_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        Stop hook - logs when agent session ends.

        Args:
            input_data: Dict with 'reason', 'num_turns', 'duration_ms'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        reason = input_data.get("reason", "unknown")
        num_turns = input_data.get("num_turns", 0)
        duration_ms = input_data.get("duration_ms", 0)

        logger.log(
            "INFO",
            "[Stop] Agent session ended",
            reason=reason,
            num_turns=num_turns,
            duration_seconds=duration_ms / 1000
        )
        return {}

    return stop_hook


def create_subagent_stop_hook(logger: ForkLogger):
    """
    Create SubagentStop hook for logging subagent completions.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def subagent_stop_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        SubagentStop hook - logs when subagent (Task tool) completes.

        Args:
            input_data: Dict with 'subagent_id'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        subagent_id = input_data.get("subagent_id", "unknown")
        logger.log(
            "INFO",
            "[SubagentStop] Subagent completed",
            subagent_id=subagent_id
        )
        return {}

    return subagent_stop_hook


def create_pre_compact_hook(logger: ForkLogger):
    """
    Create PreCompact hook for logging context compaction.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def pre_compact_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PreCompact hook - logs before context window compaction.

        Args:
            input_data: Dict with 'tokens_before'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        tokens_before = input_data.get("tokens_before", 0)
        logger.log(
            "WARNING",
            "[PreCompact] Context compaction triggered",
            tokens_before=tokens_before,
            message="Agent is compacting conversation history to fit context window"
        )
        return {}

    return pre_compact_hook


def create_hook_dict(logger: ForkLogger) -> Dict[str, Any]:
    """
    Create complete hooks dictionary for ClaudeAgentOptions.

    Registers ALL available hook types for maximum observability:
    - PreToolUse: Log and validate before tool execution
    - PostToolUse: Log tool results
    - UserPromptSubmit: Log when prompts are submitted
    - Stop: Log when agent session ends
    - SubagentStop: Log when subagents complete
    - PreCompact: Log context compaction events

    Args:
        logger: Fork logger instance

    Returns:
        Hooks dict with all hooks configured
    """
    from claude_agent_sdk import HookMatcher

    return {
        "PreToolUse": [
            HookMatcher(hooks=[create_pre_tool_hook(logger)])
        ],
        "PostToolUse": [
            HookMatcher(hooks=[create_post_tool_hook(logger)])
        ],
        "UserPromptSubmit": [
            HookMatcher(hooks=[create_user_prompt_hook(logger)])
        ],
        "Stop": [
            HookMatcher(hooks=[create_stop_hook(logger)])
        ],
        "SubagentStop": [
            HookMatcher(hooks=[create_subagent_stop_hook(logger)])
        ],
        "PreCompact": [
            HookMatcher(hooks=[create_pre_compact_hook(logger)])
        ],
    }
```

**Complete Hook Coverage:**

1. **PreToolUse Hook**:
   - Logs ALL tool calls before execution
   - Validates file paths for Read/Write/Edit (must be in temp/)
   - BLOCKS operations outside temp/ directory
   - Logs Bash commands, MCP operations

2. **PostToolUse Hook**:
   - Logs tool results (success/failure)
   - Tracks file modifications for debugging
   - Records errors with truncated output

3. **UserPromptSubmit Hook**:
   - Logs when agent receives prompts
   - Records prompt length and preview
   - Useful for tracking workflow progression

4. **Stop Hook**:
   - Logs when agent session ends
   - Records reason (max_turns, completion, error)
   - Captures total turns and duration

5. **SubagentStop Hook**:
   - Logs when Task tool subagents complete
   - Tracks subagent IDs for debugging

6. **PreCompact Hook**:
   - Logs context window compaction events
   - Records token count before compaction
   - Helps debug context management issues

**Benefits:**
- **Full Observability**: Every event is logged with structured data
- **Security**: Path validation enforced at hook level
- **Debugging**: Complete audit trail of agent behavior
- **Performance**: Track tool usage patterns and bottlenecks

### 6. Implement git_utils.py (Git Operations)
```python
# src/modules/git_utils.py

"""
Git repository utilities for validation and operations.
"""

import re
from datetime import datetime
from typing import Tuple
from .constants import DEFAULT_BRANCH_TEMPLATE


def validate_git_url(url: str) -> bool:
    """
    Validate git repository URL format.

    Args:
        url: Git repository URL

    Returns:
        True if valid, False otherwise
    """
    # Check for common git URL patterns:
    # - https://github.com/user/repo
    # - https://github.com/user/repo.git
    # - git@github.com:user/repo.git
    # Use regex to validate
    pass


def parse_repo_name(url: str) -> str:
    """
    Extract repository name from URL.

    Args:
        url: Git repository URL

    Returns:
        Repository name (e.g., "myrepo")
    """
    # Remove .git suffix if present
    # Extract last path component
    # Return repo name
    pass


def generate_branch_name() -> str:
    """
    Generate unique branch name with timestamp.

    Returns:
        Branch name string
    """
    # Get current timestamp
    # Format using DEFAULT_BRANCH_TEMPLATE
    # Return generated name
    pass


def validate_branch_name(branch: str) -> bool:
    """
    Validate branch name format.

    Args:
        branch: Branch name to validate

    Returns:
        True if valid, False otherwise
    """
    # Check for valid git branch name characters
    # No spaces, special characters except -_/
    # Use regex
    pass
```

### 7. Create System Prompt (sandbox_fork_agent_system_prompt.md)
```markdown
# src/prompts/sandbox_fork_agent_system_prompt.md

# Sandbox Fork Agent System Prompt

You are a Claude Code agent operating in a **hybrid environment**:
1. **E2B Cloud Sandbox** - For repository operations (primary)
2. **Local temp/ directory** - For temporary local files only (restricted)

Your mission is to execute the user's prompt using sandbox operations for all repository work.

## Available Tools

### 🔷 MCP Sandbox Tools (Primary - Use for Repository Operations)

Use these tools for ALL operations on the cloned repository:

- `mcp__e2b__execute_command` - Run commands in sandbox (git, npm, python, etc.)
- `mcp__e2b__write_file` - Write files to sandbox filesystem
- `mcp__e2b__read_file` - Read files from sandbox
- `mcp__e2b__list_files` - List files in sandbox directories
- `mcp__e2b__make_directory` - Create directories in sandbox
- `mcp__e2b__remove_file` - Delete files in sandbox
- `mcp__e2b__rename_file` - Rename/move files in sandbox
- `mcp__e2b__check_file_exists` - Check if sandbox file exists
- `mcp__e2b__get_file_info` - Get file metadata from sandbox

### 🔶 Local Tools (Secondary - temp/ directory ONLY)

These tools are available but **RESTRICTED to temp/ directory only**:

- `Read` - Read local files (ONLY from temp/)
- `Write` - Write local files (ONLY to temp/)
- `Edit` - Edit local files (ONLY in temp/)
- `Bash` - Execute local commands (for local-only operations)
- `WebFetch` / `WebSearch` - Fetch web content
- `Task` / `Skill` / `SlashCommand` - Utility tools

**IMPORTANT**: If you try to use Read/Write/Edit outside temp/, you will get an error. Hooks enforce this restriction for security.

## Working Environment

- **Sandbox**: Isolated E2B cloud sandbox at `/home/user/repo` (in sandbox)
- **Repository**: Git repository cloned to sandbox `/home/user/repo`
- **Local temp/**: Local directory for temporary files (restricted)
- **Working Directory**: `apps/sandbox_agent_working_dir/`

## Execution Guidelines

### For Repository Operations (99% of work):

1. **Use MCP sandbox tools**:
   ```
   mcp__e2b__execute_command(command="git status", cwd="/home/user/repo")
   mcp__e2b__read_file(path="/home/user/repo/README.md")
   mcp__e2b__write_file(path="/home/user/repo/newfile.py", content="...")
   ```

2. **Git operations in sandbox**:
   ```
   mcp__e2b__execute_command(command="git add .", cwd="/home/user/repo")
   mcp__e2b__execute_command(command="git commit -m 'message'", cwd="/home/user/repo")
   ```

3. **Package installation in sandbox**:
   ```
   mcp__e2b__execute_command(command="npm install express", cwd="/home/user/repo")
   mcp__e2b__execute_command(command="pip install requests", cwd="/home/user/repo")
   ```

### For Local temp/ Operations (rare):

Only use local tools when you need to:
- Store temporary notes or analysis files locally
- Create local scratch files for processing

**ALWAYS use paths starting with `temp/`**:
```
Write(file_path="temp/notes.txt", content="My notes")
Read(file_path="temp/analysis.json")
```

## Error Handling

- **Path Restriction Error**: If you see "Path outside temp/", use MCP sandbox tools instead
- **Sandbox Errors**: Check command output and adjust your approach
- **Tool Not Found**: Ensure you're using the correct tool for the operation

## Your Task

Execute the user's prompt below. Use sandbox operations for repository work and temp/ for any local files.

---

**USER PROMPT:**
```

### 8. Implement agents.py (Agent Management)
```python
# src/modules/agents.py

"""
Claude Code agent creation and execution for sandbox forks.
"""

import asyncio
import threading
from pathlib import Path
from typing import Optional
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ResultMessage,
)
from .logs import ForkLogger
from .hooks import create_hook_dict
from .constants import (
    SYSTEM_PROMPT_PATH,
    MCP_CONFIG_PATH,
    DEFAULT_MAX_TURNS,
    ALLOWED_TOOLS,
    DISALLOWED_TOOLS,
    WORKING_DIR,
)


class SandboxForkAgent:
    """
    Claude Code agent that executes user prompt in an isolated sandbox.

    Features:
    - Hybrid tool access (MCP + local with restrictions)
    - Full observability through hooks
    - Path gating for local file operations
    """

    def __init__(
        self,
        fork_num: int,
        repo_url: str,
        branch: str,
        user_prompt: str,
        logger: ForkLogger,
    ):
        """
        Initialize sandbox fork agent.

        Args:
            fork_num: Fork number (1-indexed)
            repo_url: Git repository URL to clone
            branch: Git branch to checkout
            user_prompt: User's prompt to execute
            logger: Logger instance for this fork
        """
        # Store all parameters
        self.fork_num = fork_num
        self.repo_url = repo_url
        self.branch = branch
        self.user_prompt = user_prompt
        self.logger = logger

        # Load system prompt from file
        system_prompt_base = self._load_system_prompt()

        # Append user prompt to system prompt
        self.full_system_prompt = self._build_full_prompt(
            system_prompt_base, user_prompt
        )

        # Build hooks for observability and path gating
        hooks_dict = create_hook_dict(logger)

        # Build ClaudeAgentOptions with:
        #   - system_prompt (loaded + user prompt)
        #   - mcp_servers from MCP_CONFIG_PATH
        #   - allowed_tools (ALLOWED_TOOLS - MCP + local)
        #   - disallowed_tools (DISALLOWED_TOOLS)
        #   - hooks (ALL hooks for full observability)
        #   - permission_mode="acceptEdits"
        #   - max_turns=DEFAULT_MAX_TURNS
        #   - cwd=WORKING_DIR
        self.options = ClaudeAgentOptions(
            system_prompt=self.full_system_prompt,
            mcp_servers=str(MCP_CONFIG_PATH),  # Path to .mcp.json
            allowed_tools=ALLOWED_TOOLS,
            disallowed_tools=DISALLOWED_TOOLS,
            hooks=hooks_dict,  # Install all hooks
            permission_mode="acceptEdits",
            max_turns=DEFAULT_MAX_TURNS,
            cwd=str(WORKING_DIR),
        )

    def _load_system_prompt(self) -> str:
        """
        Load system prompt from markdown file.

        Returns:
            System prompt text
        """
        # Read SYSTEM_PROMPT_PATH
        # Return content as string
        pass

    def _build_full_prompt(self, user_prompt: str) -> str:
        """
        Build full system prompt with user prompt appended.

        Args:
            user_prompt: User's prompt

        Returns:
            Complete system prompt
        """
        # Load system prompt
        # Append user prompt section
        # Return combined prompt
        pass

    async def execute(self) -> dict:
        """
        Execute the agent in the sandbox.

        Returns:
            Execution result with status, cost, tokens, etc.
        """
        # Log start of execution
        # Create ClaudeSDKClient with options
        # Connect to client
        # Query with repo clone instructions + user prompt
        # Stream messages and log each:
        #   - AssistantMessage -> log text blocks
        #   - ToolUseBlock -> log tool usage
        #   - ResultMessage -> extract cost/tokens
        # Handle errors and log them
        # Disconnect client
        # Return execution summary
        pass

    def _log_message(self, message):
        """
        Log agent message to fork logger.

        Args:
            message: Message from agent
        """
        # Check message type
        # If AssistantMessage: log text blocks
        # If ToolUseBlock: log tool name and input
        # If SystemMessage: log system info
        # If ResultMessage: log completion with stats
        pass


def run_fork_in_thread(
    fork_num: int,
    repo_url: str,
    branch: str,
    user_prompt: str,
    logger: ForkLogger,
) -> dict:
    """
    Run a single fork agent in a thread.

    Args:
        fork_num: Fork number
        repo_url: Git repository URL
        branch: Git branch
        user_prompt: User's prompt
        logger: Fork logger

    Returns:
        Execution result dictionary
    """
    # Create SandboxForkAgent
    # Create new event loop for this thread
    # Set event loop
    # Run agent.execute() in event loop
    # Close event loop
    # Return result
    pass


def run_forks_parallel(
    num_forks: int,
    repo_url: str,
    branch: str,
    user_prompt: str,
    log_manager,
) -> list[dict]:
    """
    Run multiple forks in parallel threads.

    Args:
        num_forks: Number of forks to run
        repo_url: Git repository URL
        branch: Git branch
        user_prompt: User's prompt
        log_manager: LogManager instance

    Returns:
        List of execution results (one per fork)
    """
    # Create list to store threads
    # Create list to store results
    # For each fork number (1 to num_forks):
    #   - Create logger from log_manager
    #   - Create thread with run_fork_in_thread
    #   - Start thread
    #   - Add to threads list
    # Wait for all threads to complete (join)
    # Collect results from all threads
    # Return results
    pass
```

### 9. Implement Main CLI Entry (main.py)
```python
# src/main.py

"""
Main CLI entry point for obox (sandbox workflows).
"""

import typer
from rich.console import Console
from . import commands

# Initialize Typer app
app = typer.Typer(
    name="obox",
    help="Orchestrated Sandbox Workflows - Multi-agent experimentation with E2B sandboxes",
    add_completion=False,
)

# Initialize Rich console for pretty output
console = Console()

# Register commands
app.command(name="sandbox-fork")(commands.sandbox_fork.sandbox_fork_command)

if __name__ == "__main__":
    app()
```

### 10. Implement sandbox_fork.py (Main Command)
```python
# src/commands/sandbox_fork.py

"""
Sandbox fork command implementation.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional
import subprocess
from ..modules import (
    constants,
    logs,
    agents,
    git_utils,
)

console = Console()


def sandbox_fork_command(
    repo_url: str = typer.Argument(..., help="Git repository URL to clone"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Git branch to checkout"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt text or path to prompt file"),
    forks: int = typer.Option(constants.DEFAULT_FORKS, "--forks", "-f", help="Number of forks to create"),
):
    """
    Fork a git repository into multiple sandboxes and run agents in parallel.

    Creates N isolated E2B sandboxes, clones the repository into each,
    and runs a Claude Code agent with the given prompt. All execution
    is logged to separate files and displayed in VSCode.
    """
    # === VALIDATION ===
    # Validate repo URL format
    # Validate fork count (1 to MAX_FORKS)
    # Generate branch name if not provided
    # Validate branch name
    # Check if prompt is a file path or text
    # If file: read file content
    # If text: use as-is

    # === SETUP ===
    # Parse repository name from URL
    # Create LogManager
    # Display startup banner with Rich
    # Show configuration table (repo, branch, forks, prompt preview)

    # === EXECUTION ===
    # Call agents.run_forks_parallel()
    # This will:
    #   - Create N threads
    #   - Initialize sandbox in each thread
    #   - Clone repo with branch
    #   - Run agent with prompt
    #   - Stream logs to files

    # === RESULTS ===
    # Collect all log file paths from LogManager
    # Display results table with:
    #   - Fork number
    #   - Status (success/error)
    #   - Log file path
    #   - Cost (if available)

    # === VSCODE INTEGRATION ===
    # Open all log files in VSCode using subprocess:
    # `code {log_file_1} {log_file_2} ... {log_file_N}`

    # === SUMMARY ===
    # Print summary:
    #   - Total forks executed
    #   - Successful forks
    #   - Failed forks
    #   - Total cost
    #   - Log directory path

    # Close all loggers
    pass
```

### 11. Create Environment Configuration Files
- Create `.env.sample` with:
  ```
  # Anthropic API Key for Claude Code agents
  ANTHROPIC_API_KEY=your_api_key_here

  # E2B API Key for sandbox management
  E2B_API_KEY=your_e2b_api_key_here
  ```
- Create `.gitignore` with:
  ```
  .env
  __pycache__/
  *.pyc
  .venv/
  logs/
  *.log
  .uv/
  ```

### 12. Create README.md Documentation
```markdown
# Sandbox Fork - Multi-Agent Git Repository Experimentation

Run parallel experiments on git repositories using isolated E2B sandboxes and Claude Code agents.

## Installation

```bash
cd apps/sandbox_workflows
uv sync
```

## Configuration

Copy `.env.sample` to `.env` and fill in your API keys:
```bash
cp .env.sample .env
```

## Usage

### Basic Fork
```bash
uv run obox sandbox-fork https://github.com/user/repo --prompt "Add unit tests to all functions"
```

### Multiple Forks
```bash
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "Refactor the codebase to use async/await" \
  --forks 5
```

### Specific Branch
```bash
uv run obox sandbox-fork https://github.com/user/repo \
  --branch feature/new-api \
  --prompt "Review and document the new API endpoints"
```

### Prompt from File
```bash
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt ./prompts/my-experiment.md \
  --forks 3
```

## How It Works

1. **Validation**: Validates repository URL, branch name, and fork count
2. **Initialization**: Creates N isolated E2B sandboxes with MCP server access
3. **Cloning**: Clones the repository into each sandbox on the specified branch
4. **Execution**: Runs a Claude Code agent in each sandbox with the given prompt
5. **Logging**: Streams all agent activity to dedicated log files (one per fork)
6. **Monitoring**: Opens all log files in VSCode for real-time progress tracking
7. **Summary**: Displays execution results with costs, tokens, and status

## Architecture

Each fork runs in complete isolation:
- Separate E2B sandbox
- Independent filesystem
- Own Claude Code agent
- Dedicated log file

### Hybrid Tool Access with Hook-Based Security

Agents operate in a **hybrid environment**:

**MCP Sandbox Tools** (Primary - for repository operations):
- ✅ `mcp__e2b__execute_command` - Run git, npm, python, etc. in sandbox
- ✅ `mcp__e2b__write_file` - Write files to sandbox
- ✅ `mcp__e2b__read_file` - Read files from sandbox

**Local Tools** (Secondary - restricted to temp/ directory):
- ✅ `Read`, `Write`, `Edit` - Local file operations (ONLY in temp/)
- ✅ `Bash` - Local commands (logged for observability)
- ✅ `WebFetch`, `WebSearch`, `Task`, etc. - Utility tools

**Hook-Based Security**:
- All tool usage is logged via hooks for full observability
- PreToolUse hook validates file paths (blocks operations outside temp/)
- Path restrictions enforced at runtime, not by disabling tools
- Cannot be bypassed - hooks run before every tool execution

## Logs

Log files are stored in `../sandbox_agent_working_dir/logs/`:
- Format: `fork-{N}-{timestamp}.log`
- Contains: All agent messages, tool usage, errors, and results
- Opens automatically in VSCode when command completes

## Examples

See `examples/` directory for sample prompts and use cases.
```

### 13. Test Project Setup
- Run `uv sync` to install dependencies
- Verify all imports resolve correctly
- Test typer CLI help: `uv run obox --help`
- Test command help: `uv run obox sandbox-fork --help`

### 14. Implement Error Handling & Validation
- Add try/except blocks in all main functions
- Validate all user inputs with clear error messages
- Handle MCP server connection errors
- Handle sandbox creation failures
- Handle git clone errors
- Add timeout handling for long-running agents

### 15. Add Rich Console Formatting
- Create beautiful tables for configuration display
- Add progress spinners for long operations
- Use color coding for success/error states
- Format cost and token displays with proper units

### 16. Integration Testing
- Test with a real git repository (use a small public repo)
- Run with 1 fork first
- Then test with 3 forks to verify parallel execution
- Verify log files are created correctly
- Verify VSCode opens with log files
- Test error scenarios (invalid repo, bad branch, etc.)

## Testing Strategy

### Unit Tests
- `test_git_utils.py`: Test URL validation, repo name parsing, branch generation
- `test_logs.py`: Test log file creation, thread-safe writing, formatting
- `test_constants.py`: Verify all paths resolve correctly

### Integration Tests
- `test_single_fork.py`: Run one fork with a simple prompt
- `test_multiple_forks.py`: Run 3 forks in parallel
- `test_error_handling.py`: Test with invalid inputs

### Manual Testing
1. Test with public repo: `https://github.com/user/simple-project`
2. Test with invalid URL: should show clear error
3. Test with non-existent branch: should show clear error
4. Test with prompt file: should read and use content
5. Test with 5 forks: verify parallel execution and unique log files

## Acceptance Criteria

- ✅ CLI command `obox sandbox-fork` is available and shows help
- ✅ Can accept repo URL, optional branch, prompt, and fork count
- ✅ Validates all inputs with clear error messages
- ✅ Creates N isolated E2B sandboxes (one per fork)
- ✅ Clones repository into each sandbox on correct branch
- ✅ Runs Claude Code agent in each sandbox with user prompt
- ✅ Agents have hybrid tool access (MCP + local with restrictions)
- ✅ ALL tool usage is logged via hooks for full observability
- ✅ Local file operations (Read/Write/Edit) are restricted to temp/ directory via hooks
- ✅ Hook path validation blocks operations outside temp/ with clear error messages
- ✅ Creates separate log file for each fork with timestamp
- ✅ Streams all agent activity (tools, prompts, results) to respective log files
- ✅ Opens all log files in VSCode automatically
- ✅ Displays summary table with fork status, log paths, and costs
- ✅ Handles errors gracefully with informative messages
- ✅ Parallel execution completes successfully

## Validation Commands

Execute these commands to validate the implementation:

```bash
# 1. Verify project structure
ls -R apps/sandbox_workflows/src/

# 2. Check dependencies installed
cd apps/sandbox_workflows && uv sync

# 3. Test CLI help
uv run obox --help

# 4. Test command help
uv run obox sandbox-fork --help

# 5. Validate imports
uv run python -c "from src.modules import constants, logs, agents, git_utils; print('All imports successful')"

# 6. Test with a real repository (single fork)
uv run obox sandbox-fork https://github.com/anthropics/anthropic-sdk-python \
  --prompt "Analyze the project structure and list all main modules" \
  --forks 1

# 7. Test with multiple forks
uv run obox sandbox-fork https://github.com/anthropics/anthropic-sdk-python \
  --prompt "Find all TODO comments and summarize them" \
  --forks 3

# 8. Verify log files created
ls -lh ../sandbox_agent_working_dir/logs/

# 9. Verify VSCode opened (check process list)
ps aux | grep code

# 10. Test hook path validation (should block)
# This would need to be tested by modifying agent to attempt access outside temp/
# Expected: Hook blocks with error "Path outside temp/"
```

## Notes

### Key Implementation Details

1. **Hook-Based Architecture**: ALL tool usage flows through hooks for complete observability and security
   - PreToolUse: Validates paths, logs tool calls
   - PostToolUse: Logs results, tracks file operations
   - UserPromptSubmit, Stop, SubagentStop, PreCompact: Full lifecycle logging
   - Path validation uses `Path.relative_to()` to check if path is within TEMP_DIR
   - Hooks cannot be bypassed - they run before every tool execution

2. **Hybrid Tool Model**: Agents have access to MCP + local tools with runtime restrictions
   - MCP tools (mcp__e2b__*): Unrestricted - operate in isolated sandbox
   - Local tools (Read/Write/Edit): Restricted to temp/ directory via hooks
   - Disallowed tools (Glob/Grep/NotebookEdit/TodoWrite): Disabled entirely
   - Benefits: More flexibility for agents while maintaining security

3. **Working Directory Structure**:
   ```
   apps/sandbox_agent_working_dir/
   ├── logs/          # Fork execution logs (separate from temp/)
   │   ├── fork-1-20250114-120000.log
   │   └── fork-2-20250114-120000.log
   └── temp/          # Local file operations (restricted by hooks)
       ├── notes.txt
       └── scratch/
   ```

4. **Thread Safety**: Use `threading.Lock()` in ForkLogger for thread-safe log writing

5. **MCP Server Path**: The MCP config at `.mcp.json` must be referenced correctly in ClaudeAgentOptions

6. **Event Loop Per Thread**: Each thread needs its own asyncio event loop for ClaudeSDKClient

7. **System Prompt Loading**: Load from file and append user prompt dynamically

8. **VSCode Integration**: Use `subprocess.run(["code", *log_paths])` to open files

9. **Error Context**: Include fork number in all error messages for debugging

10. **Timeout Handling**: Set reasonable timeouts for sandbox operations

11. **Resource Cleanup**: Always close loggers and sandbox clients in finally blocks

### Dependencies to Add

```bash
# In apps/sandbox_workflows/
uv add typer[all] rich claude-agent-sdk python-dotenv e2b
```

### Environment Variables Required

- `ANTHROPIC_API_KEY` - For Claude Code agents
- `E2B_API_KEY` - For E2B sandbox creation

### Working Directory Structure

```
apps/sandbox_agent_working_dir/temp/
└── logs/
    ├── fork-1-20250114-120000.log
    ├── fork-2-20250114-120000.log
    └── fork-3-20250114-120000.log
```

### MCP Server Configuration

The agent will use the MCP server defined in `.mcp.json` which wraps the E2B sandbox CLI. Ensure this file exists and has the correct configuration for the `e2b` server with all sandbox tools registered.
