# Agent Working Directory

Configuration directory for agents running in the obox parallel workflows system.

## Purpose

This directory contains **version-controlled configuration** for agents:
- Claude Code settings (`.claude/`)
- MCP server configuration templates (`.mcp.json*`)
- Environment variable templates (`.env.sample`)

**Runtime data** (logs, generated files) is stored in `runtime/agent_workspaces/` (gitignored).

## Structure

```
working_dir/
├── .claude/
│   └── commands/        # Custom slash commands for agents
│       ├── plan.md      # Generate implementation plans
│       ├── build.md     # Build from plans
│       └── wf_plan_build.md  # Combined plan+build workflow
├── temp/                # Agent scratch space (gitignored)
├── .gitignore           # Ignores temp/ directory
└── README.md            # This file
```

## Setup

### 1. Copy Configuration Templates

For agents to work, they need MCP and environment configuration:

```bash
# From project root
cp .mcp.json working_dir/.mcp.json
cp .env working_dir/.env
```

### 2. Configure MCP Server

Edit `working_dir/.mcp.json` to ensure it points to the correct MCP server:

```json
{
  "mcpServers": {
    "e2b-sandbox": {
      "command": "uv",
      "args": ["--directory", "../mcp", "run", "server.py"],
      "env": {
        "E2B_API_KEY": "your-e2b-api-key-here"
      }
    }
  }
}
```

### 3. Configure Environment

Edit `working_dir/.env` with your credentials:
```bash
E2B_API_KEY=your_e2b_api_key
CLAUDE_CODE_OAUTH_TOKEN=your_claude_oauth_token
GITHUB_TOKEN=your_github_token  # Optional
```

## Available Slash Commands

Agents have access to custom slash commands in `.claude/commands/`:

### `/plan <user-prompt>`
Generate a detailed implementation plan and save to specs directory.

**Example:**
```
/plan Add user authentication with JWT tokens
```

Creates a comprehensive plan file in `runtime/agent_workspaces/specs/`.

### `/build <path-to-plan>`
Build implementation from a plan file.

**Example:**
```
/build specs/add-user-authentication.md
```

Executes the plan step-by-step.

### `/wf_plan_build <user-prompt>`
Complete plan-and-build workflow in one command.

**Example:**
```
/wf_plan_build Add user authentication with JWT tokens
```

Combines `/plan` and `/build` for end-to-end feature development.

## Runtime vs Configuration

### Version Controlled (this directory)
- ✅ `.claude/` - Agent settings and slash commands
- ✅ `README.md` - Documentation

### Gitignored
- ❌ `temp/` - Agent scratch space in working directory
- ❌ `runtime/agent_workspaces/logs/` - Execution logs
- ❌ `runtime/agent_workspaces/specs/` - Generated specification files
- ❌ `runtime/agent_workspaces/temp/` - Temporary runtime files

## Usage with obox

When running parallel agent workflows with obox:

```bash
cd apps/obox
uv run obox <repo-url> --prompt "your task" --forks 3
```

Each agent fork:
1. Uses configuration from this directory (`working_dir/`)
2. Writes logs to `runtime/agent_workspaces/logs/`
3. Generates specs in `runtime/agent_workspaces/specs/`
4. Creates temp files in `working_dir/temp/` or `runtime/agent_workspaces/temp/`

## Adding Custom Slash Commands

To add a new slash command:

1. Create a markdown file in `.claude/commands/`:
   ```bash
   touch .claude/commands/my_command.md
   ```

2. Add command definition:
   ```markdown
   # My Custom Command

   Description of what this command does.

   ## Implementation

   - Step 1: ...
   - Step 2: ...
   ```

3. Use in agent prompts:
   ```bash
   uv run obox <repo-url> --prompt "/my_command do something"
   ```

## Related Documentation

- [obox README](../obox/README.md) - Parallel agent workflows
- [Runtime README](../../runtime/README.md) - Runtime data directory
- [Main README](../../README.md) - Project overview
- [Environment Setup](../.env.example) - Environment variable template
- [MCP Setup](../.mcp.json.example) - MCP configuration template
