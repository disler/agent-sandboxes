# Runtime Directory

This directory contains runtime data generated during agent execution. All contents are **gitignored** and should not be committed to version control.

## Purpose

Separates runtime/generated data from source code and configuration:
- **Version Controlled**: `apps/working_dir/` contains agent configuration (`.claude/`, `.mcp.json` templates)
- **Runtime (this directory)**: Contains logs, generated specs, temp files from agent execution

## Structure

```
runtime/
└── agent_workspaces/
    ├── logs/       # Agent execution logs
    ├── specs/      # Generated specification files
    └── temp/       # Temporary files during execution
```

## Usage

### Logs

Agent execution logs are written to `agent_workspaces/logs/` with the format:
```
{branch}-fork-{fork_num}-{timestamp}.log
```

**Examples:**
- `main-fork-1-20251124-150626.log` - Fork 1 execution on main branch
- `feature-test-fork-2-20251124-151230.log` - Fork 2 execution on feature-test branch

### Specs

Generated specification files from `/plan` slash commands are written to `agent_workspaces/specs/`.

### Temp

Temporary files created during agent operations.

## Cleanup

Since all contents are gitignored, you can safely delete this directory to clean up:

```bash
# Remove all runtime data
rm -rf runtime/

# Runtime directories will be recreated automatically on next agent run
```

## Configuration

Runtime paths are configured in `apps/obox/src/modules/constants.py`:
- `RUNTIME_DIR` - Base runtime directory
- `LOG_DIR` - Log file location
- `SPECS_DIR_RUNTIME` - Generated specs location
- `TEMP_DIR` - Temporary files location

## Why Separate Runtime from Config?

**Benefits:**
1. **Clean version control** - No accidental commits of logs or generated files
2. **Clear separation** - Config vs. data is obvious
3. **Easy cleanup** - Delete `runtime/` without affecting configuration
4. **Multi-tenancy ready** - Could support multiple agent workspaces
5. **Better organization** - Agent config stays in `apps/working_dir/`

## Related Documentation

- [Working Directory README](../apps/working_dir/README.md) - Agent configuration
- [obox README](../apps/obox/README.md) - Parallel agent workflows
- [Constants](../apps/obox/src/modules/constants.py) - Path configuration
