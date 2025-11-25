# Purpose

Quickly prime yourself on the obox (Orchestrated SandBox Agent) command-line tool and sandbox fork workflow system. Learn how to run parallel agent forks in isolated E2B sandboxes for experimentation and testing.

## Instructions

- Focus on understanding the obox command workflow, not implementation details
- Run help commands to see available options and usage
- Read only essential configuration files (agents.py, constants.py, system prompt)
- Understand that each fork runs in its own isolated E2B sandbox with full Claude SDK access
- Each fork agent operates in `working_dir/` as its working directory, but primarily uses the sandbox tools to work on the codebase in their own sandbox.
- Each fork writes detailed logs to `runtime/agent_workspaces/logs/[branch]-[fork-num]-[timestamp].log`
  - Check these to understand the work of each fork.
- Agents have access to custom slash commands in `working_dir/.claude/commands/`
- Do NOT read all source code - focus on architecture and usage

## Workflow

1. Read `@apps/obox/README.md`
2. Run `cd apps/obox && uv run obox --help`
4. Read `@apps/obox/src/prompts/sandbox_agent_system_prompt.md`
5. Follow the `Report` section to report your understanding

## Report

**Ready to work with obox workflows!** Summarize your understanding of the obox tool for running agent sandboxes in isolated E2B sandboxes.
