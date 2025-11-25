#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Run Claude Code inside an E2B Sandbox.

This minimal example creates an E2B sandbox with Claude Code pre-installed,
sends a prompt to generate a hello-world index.html, and prints the output.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root (two directories up)
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Create sandbox
sbx = Sandbox.create(
    envs={"CLAUDE_CODE_OAUTH_TOKEN": os.getenv("CLAUDE_CODE_OAUTH_TOKEN")},
    timeout=60 * 5,  # 5 minutes
)
print(f"Sandbox created: {sbx.sandbox_id}")

print("Install Claude Code...")
result = sbx.commands.run("npm install -g @anthropic-ai/claude-code tsx")
print(result.stdout)

# Run a prompt with Claude Code
print("\nRunning Claude Code with prompt...")
result = sbx.commands.run(
    "echo 'Create a hello world index.html' | claude -p --dangerously-skip-permissions",
    timeout=0,  # allow long-running commands
)
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Clean up
sbx.kill()
print("Sandbox terminated")
