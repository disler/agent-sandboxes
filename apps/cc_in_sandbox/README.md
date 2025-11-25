# Claude Code in Sandbox (Example)

**Note**: This is a reference implementation showing how to run Claude Code CLI entirely inside an E2B sandbox. For most use cases, use **[obox](../obox/)** instead, which orchestrates agents from your local machine.

## What This Does

This minimal example demonstrates running Claude Code **inside** an E2B sandbox:

1. Creates an E2B sandbox
2. Installs Claude Code CLI inside the sandbox
3. Runs a Claude Code prompt inside the sandbox
4. Terminates the sandbox

## When to Use This vs OBOX

| Feature | This (cc_in_sandbox) | OBOX |
|---------|---------------------|------|
| **Claude runs** | Inside sandbox | On your local machine |
| **Repo location** | Inside sandbox | Inside sandbox |
| **Tool access** | Local to sandbox only | Hybrid (MCP + local) |
| **Observability** | Limited (stdout/stderr) | Full (hooks, logs, VSCode) |
| **Parallelization** | Manual | Built-in (1-100 forks) |
| **Cost tracking** | Manual | Automatic |
| **Best for** | Learning, simple scripts | Production workflows |

**Recommendation**: Use **[obox](../obox/)** for real workflows. Use this example to understand how Claude Code can run inside sandboxes.

## Architecture

```
┌─────────────────────────────────────────┐
│  Your Machine                           │
│                                         │
│  Python Script (this file)              │
│  └─ Creates sandbox via E2B SDK        │
│     └─ Sends commands to sandbox       │
└─────────────────┬───────────────────────┘
                  │ E2B SDK
                  ▼
┌─────────────────────────────────────────┐
│  E2B Cloud Sandbox                      │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ Claude Code CLI (installed)        │ │
│  │  - Runs prompts                    │ │
│  │  - Edits files                     │ │
│  │  - Executes commands               │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**vs OBOX Architecture:**

```
┌─────────────────────────────────────────┐
│  Your Machine (obox)                    │
│                                         │
│  Claude Code Agent (SDK)                │
│  └─ Uses MCP tools to control sandbox  │
└─────────────────┬───────────────────────┘
                  │ MCP Protocol
                  ▼
┌─────────────────────────────────────────┐
│  E2B Cloud Sandbox                      │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ Your cloned repository             │ │
│  │  - Files                           │ │
│  │  - Git history                     │ │
│  │  - Commands executed remotely      │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Setup

```bash
# Ensure .env file exists in repository root with:
# - CLAUDE_CODE_OAUTH_TOKEN (get via: claude setup-token)
# - E2B_API_KEY (get from: https://e2b.dev/docs)

# The script uses uv's inline script dependencies
# No additional installation needed
```

## Usage

```bash
# Run the example
uv run apps/cc_in_sandbox/run_claude_in_sandbox.py
```

**What happens:**
1. Creates E2B sandbox (5 minute timeout)
2. Installs Claude Code CLI via npm
3. Runs a prompt: "Create a hello world index.html"
4. Prints Claude Code's output
5. Terminates the sandbox

## Key Code

```python
# Create sandbox with Claude token
sbx = Sandbox.create(
    envs={"CLAUDE_CODE_OAUTH_TOKEN": os.getenv("CLAUDE_CODE_OAUTH_TOKEN")},
    timeout=60 * 5,
)

# Install Claude Code
sbx.commands.run("npm install -g @anthropic-ai/claude-code tsx")

# Run Claude Code with a prompt
sbx.commands.run(
    "echo 'Create a hello world index.html' | claude -p --dangerously-skip-permissions",
    timeout=0,
)

# Clean up
sbx.kill()
```

## Limitations

- **No observability**: Can't see Claude Code's thinking, tool usage, or detailed logs
- **No parallelization**: Must manually create multiple sandboxes for parallel execution
- **No cost tracking**: Must manually track API usage and costs
- **No hook system**: Can't intercept or validate tool calls
- **Basic error handling**: Only gets stdout/stderr, not structured errors
- **Manual cleanup**: Must remember to kill sandbox

## When This Approach Makes Sense

✅ **Good for:**
- Learning how Claude Code works in sandboxes
- Simple one-off scripts
- Testing Claude Code installation in sandboxes
- Understanding the E2B SDK

❌ **Use OBOX instead for:**
- Production workflows
- Parallel experiments
- Cost tracking and reporting
- Full observability and logging
- Complex multi-step tasks
- Repository analysis and editing

## Extending This Example

If you want to build on this pattern:

1. **Add repository cloning**: Clone a git repo before running Claude Code
2. **Install dependencies**: Run npm/pip install before Claude Code runs
3. **Multiple prompts**: Send multiple prompts sequentially
4. **File retrieval**: Download generated files from sandbox
5. **Parallel execution**: Create multiple sandboxes in threads

But remember: **OBOX already does all of this** with better observability, error handling, and parallelization!

## See Also

- **[OBOX](../obox/)** - Recommended tool for production workflows
- **[CLI](../cli/)** - Direct E2B sandbox control
- **[MCP](../mcp/)** - Use E2B sandboxes in Claude Desktop

## Resources

- E2B SDK: https://e2b.dev/docs
- Claude Code: https://www.claude.com/product/claude-code
- E2B Python SDK: https://github.com/e2b-dev/e2b
