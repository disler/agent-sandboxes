# Agent Sandboxes
>
> Here we explore e2b agent sandboxes and claude code together to scale your agentic engineering.
>
> Watch the full video where we break down agent sandboxes and claude code [here](https://youtu.be/1ECn5zrVUB4)

Using Agent Sandboxes (E2B) for complete agentic engineering control.

<img src="images/agent_sandboxes_snapshot.png" alt="Agent Sandboxes Architecture Diagram" width="800">

## Value Proposition
> 
> Agent Sandboxes unlock 3 key capabilities for your agentic engineering:

- **Isolation**: Each agent fork runs in a fully isolated, gated E2B sandbox, this means no matter what your agent does, it's secure and safe from your local filesystem and production environment.
- **Scale**: You can run as many agent forks as you want, each fork is independent and has its own sandbox. This is a very literal way to scale your compute to scale your impact.
- **Agency**: Your agents have full control over the sandbox environment, they can install packages, modify files, run commands, etc. This means they can handle more of the engineering process for you.

## Apps

- `sandbox_workflows/` - **obox**: Run parallel agent forks in isolated E2B sandboxes for experimentation
- `sandbox_mcp/` - MCP server wrapping sandbox_cli for LLM integration (works from root)
- `sandbox_cli/` - Click CLI for E2B sandbox management (init, exec, files, lifecycle)
- `sandbox_fundamentals/` - E2B SDK learning examples and patterns
- `cc_in_sandbox/` - Run Claude Code agent inside an E2B sandbox (ibox: in box agent)
- `sandbox_agent_working_dir/` - Agent runtime working directory

## Agent Sandbox Tooling Choice

Using **[e2b](https://e2b.dev/)** (General Sandbox SDK) for:
- Full control over sandbox environment
- Shell command execution
- File system operations
- Running tools (Claude Code, git, npm, etc.)

## Quick Start

### 1. Global Environment Setup

Create a `.env` file in the project root with the following API keys:

```bash
# Required for all sandbox operations
E2B_API_KEY=your_e2b_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Required for git push/PR functionality
GITHUB_TOKEN=your_github_token_here
```

**Install the top Agentic Coding Tool:**
- **Claude Code**: [https://www.claude.com/product/claude-code](https://www.claude.com/product/claude-code)

**Get your API keys:**
- **E2B API Key**: [https://e2b.dev/docs](https://e2b.dev/docs) - Sign up and get your API key
- **Anthropic API Key**: [https://console.anthropic.com/](https://console.anthropic.com/) - Create an API key in your account settings
- **GitHub Token**: [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) - Create a personal access token with `repo` scope

### 2. Application Usage

I recommend working from the atoms of the codebase (e2b fundamentals, cli, mcp) to the full e2e sandbox workflow (obox workflows).

**Process:**
1. Setup environment variables
2. Explore E2B Fundamentals `apps/sandbox_fundamentals/`
3. Explore E2B CLI `apps/sandbox_cli/`
4. Explore E2B MCP `apps/sandbox_mcp/`
5. Explore E2B Workflow `apps/sandbox_workflows/`

#### Explore E2B Fundamentals - `apps/sandbox_fundamentals/`

> **Start Here**

Recommended: Walk through all example scripts to understand E2B sandbox concepts.

```bash
cd apps/sandbox_fundamentals
uv sync

# Run through all examples in order
uv run python 01_basic_sandbox.py
uv run python 01_basic_sandbox_keep_alive.py
uv run python 02_list_files.py
uv run python 03_file_operations.py
uv run python 04_run_commands.py
uv run python 05_environment_vars.py
uv run python 06_background_commands.py
uv run python 07_reuse_sandbox.py
uv run python 08_pause_resume.py
uv run python 09_claude_code_agent.py
uv run python 10_install_packages.py
uv run python 11_git_operations.py
uv run python 12_custom_template_build.py
uv run python 12_custom_template_reuse.py
uv run python 13_expose_simple_webserver.py
uv run python 13_expose_vite_vue_webserver.py
```

#### Use CLI for Sandbox Management - `apps/sandbox_cli/`
```bash
cd apps/sandbox_cli
uv sync

# Get help
uv run python src/main.py --help

# Initialize a new sandbox
uv run python src/main.py init

# Create a sandbox with custom template (this is an e2b sandbox template - you can create this by running the `uv run python 12_custom_template_build.py` script)
uv run python src/main.py sandbox create --template agent-sandbox-dev-node22

# Execute a command in a sandbox
uv run python src/main.py exec <sandbox-id> "ls -la"

# List files in a sandbox
uv run python src/main.py files ls <sandbox-id> /
```

You can also boot up a claude code agent and run `/prime_cli_sandbox.md` - then prompt your agent to run the commands for you.

#### Use MCP Server with Claude Desktop - `apps/sandbox_mcp/`
Works from project root - MCP server is configured in your Claude Desktop config.
```bash
# cp the .mcp.json.sandbox to .mcp.json
cp .mcp.json.sandbox .mcp.json

# replace your e2b api key in the .mcp.json env section
...

# Start a claude code agent with the .mcp.json
claude

# Check the mcp server status
/mcp

# Prompt the same commands as you would with the sandbox_cli with natural language
prompt: What can we do with the e2b sandbox tools?

prompt: init a new sandbox

prompt: create a sandbox with custom template agent-sandbox-dev-node22

prompt: run ls -la in the sandbox

prompt: search for all .py files in the sandbox with exec

# Run custom slash commands
prompt: /plan Add buttons to the nav bar that auto scroll to respective sections on the landing page

prompt: /build <path-to-plan>

prompt: /wf_plan_build Add buttons to the nav bar that auto scroll to respective sections on the landing page

```

#### Run Parallel Agent Experiments - **obox** - `apps/sandbox_workflows/`
```bash
cp .mcp.json apps/sandbox_agent_working_dir/.mcp.json (after you fill it out with your e2b api key)
cp .env apps/sandbox_agent_working_dir/.env (after you fill it out with your credentials)

cd apps/sandbox_workflows
uv sync
uv run obox <repo-url> --branch <branch> --model <opus|sonnet|haiku> --prompt "your task" --forks 3
```

You can also boot up a claude code agent and run `/prime_obox.md` - then prompt your agent to run the commands for you.

See `apps/*/README.md` for detailed documentation on each tool.

## Application Notes

### obox - `apps/sandbox_workflows/`

- There are two system prompts for the custom agent that drives the sandbox engineering
  - `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_w_github_token_system_prompt.md` - Supports GitHub token auth for git push/PR functionality
  - `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_system_prompt.md` - Basic system prompt for sandbox engineering, does not have git push/PR functionality
  - You can either use specific prompt workflows (see `apps/sandbox_agent_working_dir/.claude/commands/wf_plan_build.md`) to manage git operations, or you can use the system prompt.
- The agents working directory is `apps/sandbox_agent_working_dir/` see `apps/sandbox_workflows/src/modules/constants.py` for more details.
  - That means that `apps/sandbox_agent_working_dir/./claude/commands/` are the available slash commands for the agent (and all the other claude capabilities are active there too)

## Resources

- https://e2b.dev/
- https://www.claude.com/product/claude-code
- https://docs.claude.com/en/docs/agent-sdk/python
- See `ai_docs/README.md` for resources used to build this codebase.

## Master **Agentic Coding**
> Prepare for the future of software engineering

Learn tactical agentic coding patterns with [Tactical Agentic Coding](https://agenticengineer.com/tactical-agentic-coding?y=agsbx)

Follow the [IndyDevDan YouTube channel](https://www.youtube.com/@indydevdan) to improve your agentic coding advantage.

