# Agent Sandboxes
>
> Scale your agentic engineering with E2B sandboxes and Claude Code
>

## Why Agent Sandboxes?

Agent Sandboxes unlock 3 key capabilities for your agentic engineering:

- **Isolation**: Each agent fork runs in a fully isolated, gated E2B sandbox. No matter what your agent does, it's secure and safe from your local filesystem and production environment.
- **Scale**: Run as many agent forks as you want in parallel. Each fork is independent with its own sandbox. This is a literal way to scale your compute to scale your impact.
- **Agency**: Your agents have full control over the sandbox environment - install packages, modify files, run commands, etc. They can handle more of the engineering process for you.

## Quick Start with OBOX

**OBOX** (Orchestrated Sandbox) is the main tool - it runs parallel Claude Code agent experiments on git repositories using isolated E2B sandboxes.

### 1. Setup (One Time)

**Get your API keys:**
- **E2B API Key**: [https://e2b.dev/docs](https://e2b.dev/docs)
- **Claude Code OAuth Token**: Run `claude setup-token` or get from [https://claude.ai/settings](https://claude.ai/settings)
- **GitHub Token** (optional): [Create personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

**Configure environment:**

```bash
# Step 1: Setup environment variables
cp .env.example .env

# Edit .env file and add your API keys
# Required: E2B_API_KEY, CLAUDE_CODE_OAUTH_TOKEN (or ANTHROPIC_API_KEY)
# Optional: GITHUB_TOKEN

# Step 2: Setup MCP server configuration
cp working_dir/.mcp.json.example working_dir/.mcp.json

# Edit working_dir/.mcp.json and replace "your-e2b-api-key-here" with your actual E2B API key
```

> **Important**: The `.mcp.json` file contains your E2B API key and should never be committed to git (it's in `.gitignore`).

**Install dependencies:**

```bash
cd apps/obox
uv sync
```

### 2. Run Your First Experiment

```bash
# Single fork experiment
uv run obox https://github.com/user/repo \
  --prompt "Add comprehensive unit tests for all utility functions"

# Run 3 parallel experiments
uv run obox https://github.com/user/repo \
  --prompt "Refactor the authentication module to use async/await" \
  --forks 3

# Use different models
uv run obox https://github.com/user/repo \
  --prompt "Quick code review" \
  --model haiku  # Options: opus, sonnet, haiku

# Specify branch
uv run obox https://github.com/user/repo \
  --branch feature/new-api \
  --prompt "Review and document the API endpoints"
```

### 3. Monitor Execution

OBOX automatically:
- Creates isolated E2B sandboxes for each fork
- Clones your repository into each sandbox
- Runs Claude Code agents with your prompt
- Logs all activity to `runtime/agent_workspaces/logs/`
- Opens log files in VSCode for real-time monitoring
- Displays summary table with costs, tokens, and status

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Your Machine (obox)                                    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Claude Agent│  │ Claude Agent│  │ Claude Agent│   │
│  │  Thread 1   │  │  Thread 2   │  │  Thread 3   │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │           │
└─────────┼────────────────┼────────────────┼───────────┘
          │ MCP Tools      │ MCP Tools      │ MCP Tools
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│  E2B Cloud Sandboxes (isolated environments)            │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Sandbox 1  │  │  Sandbox 2  │  │  Sandbox 3  │   │
│  │             │  │             │  │             │   │
│  │ git repo    │  │ git repo    │  │ git repo    │   │
│  │ branch-1    │  │ branch-2    │  │ branch-3    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Parallel Execution**: Run 1-100 forks in parallel threads
- **Auto-Branch Generation**: Unique branches for each fork
- **Full Observability**: Detailed logs capture every tool use
- **Cost Tracking**: Per-fork and total cost/token tracking
- **Path Security**: Hook-based restrictions prevent local file access
- **Project Commands**: Agents can use custom slash commands (`/plan`, `/build`, `/wf_plan_build`)

See [apps/obox/README.md](apps/obox/README.md) for complete documentation.

## Project Structure

### Core Apps
- **[apps/obox/](apps/obox/)** - **OBOX**: Run parallel agent forks in isolated E2B sandboxes (recommended starting point)
- **[apps/mcp/](apps/mcp/)** - MCP server wrapping E2B CLI for Claude Desktop integration
- **[apps/cli/](apps/cli/)** - Command-line interface for E2B sandbox management
- **[apps/cc_in_sandbox/](apps/cc_in_sandbox/)** - Example: Run Claude Code agent inside an E2B sandbox

### Shared Libraries
- **[lib/](lib/)** - Shared library (`sandbox-common`) for configuration, logging, and utilities

### Configuration & Runtime
- `.env.example` - Environment variable template - copy to `.env` in root (and `working_dir/.env` optional)
- `working_dir/.mcp.json.example` - MCP server configuration template (copy to `working_dir/.mcp.json`)
- `working_dir/` - Agent configuration directory (slash commands, configs)
- `runtime/` - Runtime data directory (gitignored)
  - `runtime/agent_workspaces/logs/` - Agent execution logs
  - `runtime/agent_workspaces/specs/` - Generated specification files
  - `runtime/agent_workspaces/temp/` - Temporary files

## Architecture

### Claude Code in Sandbox (Example)

**Note**: This is an example/reference implementation showing how you can run Claude Code entirely inside a sandbox. For most use cases, use **obox** instead.

See [apps/cc_in_sandbox/README.md](apps/cc_in_sandbox/README.md) for details.

## Where Calude Runs

| App | Claude Execution Location | Repository Location | How It Works |
|-----|---------------------------|---------------------|--------------|
| **`obox/`** | Local machine | Inside E2B sandbox | Claude Code agent runs on your local machine but uses MCP tools to remotely operate on repositories cloned inside E2B sandboxes. Hybrid tool access: MCP for sandbox operations + local tools for permitted directories. |
| **`cc_in_sandbox/`** | Inside E2B sandbox | Inside E2B sandbox | Claude Code CLI is installed and runs directly inside the sandbox. All operations are local to the sandbox environment. |

**In summary:**
- **`obox`**: Claude lives on your machine, works on sandboxed repos (orchestrated remote execution) - **recommended**
- **`cc_in_sandbox`**: Claude lives in the sandbox (fully isolated execution) - **example/reference**

## Other Tools

### MCP Server for Claude Desktop

Use E2B sandboxes directly in Claude Desktop conversations:

```bash
cd apps/mcp

# Test with MCP Inspector
uv run mcp dev server.py

# Install for Claude Desktop
uv run mcp install server.py
```

Then in Claude Desktop:
```
"Create a Python sandbox and install pandas"
"Upload my data.csv and run analysis.py"
"Clone this repo and run the tests"
```

See [apps/mcp/README.md](apps/mcp/README.md) for complete documentation.

### CLI for Direct Sandbox Management

Direct command-line control of E2B sandboxes:

```bash
cd apps/cli
uv sync

# Initialize a sandbox
uv run sbx init
export SANDBOX_ID=$(cat .sandbox_id)

# Execute commands
uv run sbx exec $SANDBOX_ID "python --version"
uv run sbx exec $SANDBOX_ID "pip install requests" --root

# File operations
uv run sbx files write $SANDBOX_ID /home/user/test.py "print('hello')"
uv run sbx files read $SANDBOX_ID /home/user/test.py

# Run code
uv run sbx exec $SANDBOX_ID "python /home/user/test.py"
```

See [apps/cli/README.md](apps/cli/README.md) for complete documentation.

## Testing

Each app includes smoke tests to verify basic functionality:

```bash
# Test CLI
cd apps/cli
uv sync
uv run pytest tests/ -v

# Test MCP Server
cd apps/mcp
uv sync
uv run pytest tests/ -v

# Test OBOX
cd apps/obox
uv sync
uv run pytest tests/ -v
```

**Requirements**: Tests require `.env` files to be configured with valid API keys. See setup instructions above.

## Resources

- https://e2b.dev/
- https://www.claude.com/product/claude-code
- https://docs.claude.com/en/docs/agent-sdk/python

## Acknowledgements

- Forked from https://github.com/disler/agent-sandboxes by IndyDevDan
- Watch the full video walkthrough: [Agent Sandboxes with Claude Code](https://youtu.be/1ECn5zrVUB4)
- Follow the [IndyDevDan YouTube channel](https://www.youtube.com/@indydevdan) 
