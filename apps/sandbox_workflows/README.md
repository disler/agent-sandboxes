# Sandbox Fork - Multi-Agent Git Repository Experimentation

Run parallel experiments on git repositories using isolated E2B sandboxes and Claude Code agents.

## Key Features

- **Parallel Execution**: Run 1-100 forks in parallel threads with independent sandboxes
- **Model Selection**: Choose between Opus, Sonnet, or Haiku models per experiment
- **Auto-Branch Generation**: Automatically creates unique branches for each fork
- **Thread-Safe Logging**: Each fork gets its own detailed log file with all agent activity
- **Full Observability**: 6 hook types capture every tool use, prompt, result, and error
- **Path Security**: Hook-based restrictions prevent accidental local filesystem access
- **GitHub Integration**: Optional GitHub token support for automated push/PR operations
- **Project-Level Commands**: Agents have access to custom slash commands (`/plan`, `/build`, `/wf_plan_build`)
- **Cost Tracking**: Per-fork and total cost tracking with detailed token usage
- **VSCode Integration**: Auto-opens all log files for real-time monitoring

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

Edit `.env` and add:
- `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude
- `E2B_API_KEY` - Your E2B API key for sandbox management
- `GITHUB_TOKEN` (Optional) - GitHub Personal Access Token for git push/PR operations

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

### With Different Models

```bash
# Use faster Haiku model
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "Quick code review" \
  --model haiku

# Use powerful Opus model
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "Complex refactoring task" \
  --model opus
```

### With Max Turns Limit

```bash
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "Add comprehensive documentation" \
  --max-turns 50
```

## How It Works

1. **Validation**: Validates repository URL, branch name, fork count, and model
2. **Branch Generation**: Auto-generates unique branch names if not provided (with num_forks > 1, appends fork number: `branch-1`, `branch-2`, etc.)
3. **Parallel Execution**: Creates N threads, each running an isolated Claude Code agent
4. **Sandbox Initialization**: Each agent initializes its own E2B sandbox with MCP server access
5. **Repository Cloning**: Clones the repository into each sandbox on the fork-specific branch
6. **Agent Execution**: Runs agent with system prompt, user prompt, and full observability hooks
7. **Logging**: Streams all agent activity to dedicated log files (one per fork) with thread-safe logging
8. **Monitoring**: Opens all log files in VSCode for real-time progress tracking
9. **Summary**: Displays execution results table with costs, tokens, status, and log paths

## Available Slash Commands

Agents have access to custom slash commands in `../sandbox_agent_working_dir/.claude/commands/`:

- **`/plan <user-prompt>`** - Generate a detailed implementation plan and save to `specs/` directory
  - Creates comprehensive step-by-step plans with acceptance criteria
  - Includes relevant files, testing strategy, and validation commands
  - Useful for complex features that need planning before implementation

- **`/build <path-to-plan>`** - Build implementation from a plan file
  - Reads plan file from `specs/` directory
  - Executes step-by-step implementation following the plan
  - Reports progress and completion status

- **`/wf_plan_build <user-prompt>`** - Complete plan-and-build workflow
  - Combines `/plan` and `/build` in one command
  - First generates the plan, then implements it
  - Best for end-to-end feature development in a single prompt

### Example Usage

```bash
# Using /plan in a prompt
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "/plan Add user authentication with JWT tokens"

# Using /wf_plan_build for complete workflow
uv run obox sandbox-fork https://github.com/user/repo \
  --prompt "/wf_plan_build Add user authentication with JWT tokens" \
  --forks 3
```

## Architecture

### Fork Isolation

Each fork runs in complete isolation:
- **Separate Thread**: Independent Python thread with its own async event loop
- **Separate E2B Sandbox**: Isolated cloud sandbox with full filesystem and process isolation
- **Independent Branch**: Auto-generated branch name (e.g., `main-1`, `main-2`, `main-3`)
- **Own Claude Code Agent**: Dedicated ClaudeSDKClient instance with full configuration
- **Dedicated Log File**: Thread-safe logger writing to `{branch}-fork-{num}-{timestamp}.log`

### Agent Configuration

Each agent is configured with:
- **System Prompt**: Dynamically formatted with repo URL, branch, fork number, GitHub token, allowed directories
- **MCP Server Access**: Full access to E2B sandbox tools via MCP protocol
- **Allowed Tools**: Whitelisted set of 25+ tools (sandbox + local + utility)
- **Disallowed Tools**: Blacklisted tools (e.g., NotebookEdit) for security
- **Permission Mode**: Set to `acceptEdits` for autonomous operation
- **Max Turns**: Configurable (default: 100 turns)
- **Model**: Configurable (opus, sonnet, haiku)
- **Working Directory**: Set to `apps/sandbox_agent_working_dir/`
- **Setting Sources**: `["project"]` enables project-level slash commands
- **Environment**: GitHub token passed to agent environment if available

### Execution Flow

1. Main thread creates LogManager and validates inputs
2. For each fork (1 to N):
   - Create thread with unique fork number
   - Generate fork-specific branch name (`branch-{fork_num}`)
   - Create ForkLogger from LogManager
   - Create SandboxForkAgent with all configuration
   - Start thread running `run_fork_in_thread()`
3. Each thread independently:
   - Creates new async event loop
   - Initializes ClaudeSDKClient with options
   - Loads and formats system prompt
   - Connects to SDK client
   - Submits user prompt
   - Streams messages and logs to fork logger
   - Extracts cost/token data from ResultMessage
   - Returns execution result dict
4. Main thread waits for all threads to complete
5. Displays results table and opens logs in VSCode

### Hybrid Tool Access with Hook-Based Security

Agents operate in a **hybrid environment**:

**MCP Sandbox Tools** (Primary - for repository operations):
- ✅ `mcp__e2b-sandbox__execute_command` - Run git, npm, python, etc. in sandbox
- ✅ `mcp__e2b-sandbox__write_file` - Write files to sandbox
- ✅ `mcp__e2b-sandbox__read_file` - Read files from sandbox
- ✅ `mcp__e2b-sandbox__list_files` - List sandbox directory contents
- ✅ `mcp__e2b-sandbox__make_directory` - Create directories in sandbox
- ✅ `mcp__e2b-sandbox__get_host` - Get public URL for exposed ports (webservers)

**Local Tools** (Secondary - restricted to allowed directories):
- ✅ `Read`, `Write`, `Edit` - Local file operations (ONLY in allowed directories: temp/, specs/, ai_docs/, app_docs/)
- ✅ `Bash` - Local commands (logged for observability)
- ✅ `WebFetch`, `WebSearch`, `Task`, `Skill`, `SlashCommand`, `TodoWrite`, `Glob`, `Grep` - Utility tools

**Hook-Based Security & Observability**:

All hooks are registered for maximum visibility and control:
- **PreToolUse**: Logs and validates before tool execution, blocks paths outside allowed directories
- **PostToolUse**: Logs tool results and tracks file modifications
- **UserPromptSubmit**: Logs when prompts are submitted
- **Stop**: Logs when agent session ends (reason, turns, duration)
- **SubagentStop**: Logs when subagents (Task tool) complete
- **PreCompact**: Logs context window compaction events

Security features:
- Path restrictions enforced at runtime before tool execution
- Cannot be bypassed - hooks run before every tool call
- Allowed directories: temp/, specs/, ai_docs/, app_docs/
- All Bash commands logged for observability

## Logs

Log files are stored in `../sandbox_agent_working_dir/logs/`:
- Format: `{branch}-fork-{fork_num}-{timestamp}.log`
- Contains: All agent messages, tool usage, errors, and results
- Opens automatically in VSCode when command completes

## Examples

### Example 1: Add Tests to Multiple Branches

```bash
uv run obox sandbox-fork https://github.com/myorg/myrepo \
  --branch main \
  --prompt "Add comprehensive unit tests for all utility functions" \
  --forks 1
```

### Example 2: Parallel Refactoring Experiments

```bash
uv run obox sandbox-fork https://github.com/myorg/myrepo \
  --prompt "Refactor the authentication module to use modern async/await patterns" \
  --forks 3
```

### Example 3: Code Review and Documentation

```bash
uv run obox sandbox-fork https://github.com/myorg/myrepo \
  --branch feature/new-api \
  --prompt "Review the new API implementation, add JSDoc comments, and create usage examples" \
  --forks 1
```

## Project Structure

```
apps/sandbox_workflows/
├── src/
│   ├── main.py                 # CLI entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   └── sandbox_fork.py     # Main command implementation
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── constants.py        # Configuration constants
│   │   ├── logs.py             # Thread-safe logging
│   │   ├── hooks.py            # Hook implementations
│   │   ├── git_utils.py        # Git utilities
│   │   ├── forks.py            # Fork execution management
│   │   └── agents.py           # Agent management
│   └── prompts/
│       └── sandbox_fork_agent_system_prompt.md
├── pyproject.toml              # Project configuration
├── .env.sample                 # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run isort src/
```

### Type Checking

```bash
uv run mypy src/
```

## Troubleshooting

### "VSCode not found"

If VSCode doesn't open automatically, you can manually open log files from:
```
../sandbox_agent_working_dir/logs/
```

### "Invalid API key"

Make sure you've created a `.env` file with valid API keys:
```bash
cp .env.sample .env
# Edit .env with your keys
```

### "Path outside allowed directories"

If you see this error in logs, the agent tried to use local file tools (Read/Write/Edit) outside the allowed directories (temp/, specs/, ai_docs/, app_docs/). This is expected behavior - the hook blocked the operation for security. The agent should use MCP sandbox tools instead for repository operations.

## License

MIT

## Contributing

Pull requests are welcome! Please ensure all tests pass and code is formatted.
