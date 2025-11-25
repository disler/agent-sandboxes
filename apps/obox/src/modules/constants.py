"""
Configuration constants for obox (sandbox orchestration CLI).
"""

from pathlib import Path
from typing import Final

# === Project Paths ===
# Root directory of the obox project
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent

# Repository root (parent of apps/)
REPO_ROOT: Final[Path] = PROJECT_ROOT.parent.parent

# Working directory for agent configuration (version controlled, at repo root)
WORKING_DIR: Final[Path] = REPO_ROOT / "working_dir"

# Temp directory in working_dir for agent scratch space
WORKING_DIR_TEMP: Final[Path] = WORKING_DIR / "temp"

# Runtime directory for agent execution (gitignored)
RUNTIME_DIR: Final[Path] = REPO_ROOT / "runtime" / "agent_workspaces"

# Temp directory for local file operations (hooks enforce this restriction)
TEMP_DIR: Final[Path] = RUNTIME_DIR / "temp"

# Temp directory name (for logging/validation)
TEMP_DIR_NAME: Final[str] = "temp"

# Log directory for fork execution logs
LOG_DIR: Final[Path] = RUNTIME_DIR / "logs"

# Specs directory for generated specifications
SPECS_DIR_RUNTIME: Final[Path] = RUNTIME_DIR / "specs"

# MCP server configuration path (in working_dir)
MCP_CONFIG_PATH: Final[Path] = WORKING_DIR / ".mcp.json"

# System prompt file path
SYSTEM_PROMPT_PATH: Final[Path] = (
    PROJECT_ROOT / "src" / "prompts" / "sandbox_agent_system_prompt.md"
)

# Additional allowed directories for Read/Write/Edit operations
SPECS_DIR: Final[Path] = REPO_ROOT / "specs"
AI_DOCS_DIR: Final[Path] = REPO_ROOT / "ai_docs"
APP_DOCS_DIR: Final[Path] = REPO_ROOT / "app_docs"

# All allowed directories for local file operations
ALLOWED_DIRECTORIES: Final[list[Path]] = [
    WORKING_DIR_TEMP,
    TEMP_DIR,
    SPECS_DIR_RUNTIME,
    SPECS_DIR,
    AI_DOCS_DIR,
    APP_DOCS_DIR,
]

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
    "mcp__e2b-sandbox__init_sandbox",
    "mcp__e2b-sandbox__create_sandbox",
    "mcp__e2b-sandbox__connect_sandbox",
    "mcp__e2b-sandbox__execute_command",
    "mcp__e2b-sandbox__write_file",
    "mcp__e2b-sandbox__read_file",
    "mcp__e2b-sandbox__list_files",
    "mcp__e2b-sandbox__upload_file",
    "mcp__e2b-sandbox__download_file",
    "mcp__e2b-sandbox__make_directory",
    "mcp__e2b-sandbox__remove_file",
    "mcp__e2b-sandbox__rename_file",
    "mcp__e2b-sandbox__check_file_exists",
    "mcp__e2b-sandbox__get_file_info",
    "mcp__e2b-sandbox__get_host",
    "mcp__e2b-sandbox__kill_sandbox",
    "mcp__e2b-sandbox__pause_sandbox",
    "mcp__e2b-sandbox__resume_sandbox",
    # Local Tools (restricted by hooks to ALLOWED_DIRECTORIES)
    "Read",  # Hook validates path is within allowed directories
    "Write",  # Hook validates path is within allowed directories
    "Edit",  # Hook validates path is within allowed directories
    "Bash",  # Hook logs all commands for observability
    # Utility Tools
    "WebFetch",
    "WebSearch",
    "Task",
    "Skill",
    "SlashCommand",
    "TodoWrite",
    "Glob",
    "Grep",
]

# Disallowed tools (not needed for this workflow)
DISALLOWED_TOOLS: Final[list[str]] = [
    "NotebookEdit",  # Not needed for git workflows
]

# === Path Restriction Configuration ===
# Tools that require path validation (must operate within ALLOWED_DIRECTORIES)
PATH_RESTRICTED_TOOLS: Final[set[str]] = {
    "Read",
    "Write",
    "Edit",
}

# === Logging Configuration ===
# Log file name template
LOG_FILE_TEMPLATE: Final[str] = "{branch}-fork-{fork_num}-{timestamp}.log"

# Log timestamp format
LOG_TIMESTAMP_FORMAT: Final[str] = "%Y%m%d-%H%M%S"

# === Git Configuration ===
# Default branch name template if not provided
DEFAULT_BRANCH_TEMPLATE: Final[str] = "fork-experiment-{timestamp}"
