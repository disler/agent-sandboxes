#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Setup Claude Code agent in sandbox, sync version with local, run prompt.
"""

import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Claude Code Agent Setup ===\n")

# Get local Claude Code version
print("📍 Checking local Claude Code version...")
local_version = subprocess.run(
    ["claude", "--version"],
    capture_output=True,
    text=True
).stdout.strip().split()[0]
print(f"   Local version: {local_version}")

# Create sandbox with Claude Code template
print("\n🚀 Creating sandbox with Claude Code template...")
sbx = Sandbox.create(
    template='claude-code',
    envs={"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")},
    timeout=60 * 5
)
print(f"   Sandbox: {sbx.sandbox_id}")

# Check Claude Code version in sandbox
print("\n🔍 Checking Claude Code in sandbox...")
result = sbx.commands.run("claude --version")
sandbox_version = result.stdout.strip().split()[0]
print(f"   Sandbox version: {sandbox_version}")

# Update if versions don't match
if sandbox_version != local_version:
    print(f"\n⚡ Version mismatch! Updating {sandbox_version} → {local_version}")
    update_result = sbx.commands.run("claude update", timeout=120)
    print(update_result.stdout)

    # Verify update
    result = sbx.commands.run("claude --version")
    new_version = result.stdout.strip().split()[0]
    print(f"   Updated to: {new_version}")
else:
    print("   ✅ Version matches local installation")

# Run a simple ping prompt
print("\n🤖 Running Claude Code prompt...")
print("   Prompt: 'Create a simple hello.txt file with a greeting'\n")

result = sbx.commands.run(
    "echo 'Create a simple hello.txt file with a greeting' | claude -p --dangerously-skip-permissions",
    timeout=0
)

print("📄 Claude Code response:")
print(result.stdout)

# Verify the file was created
print("\n✅ Verifying output...")
if sbx.files.exists("/home/user/hello.txt"):
    content = sbx.files.read("/home/user/hello.txt")
    print(f"   ✓ File created: /home/user/hello.txt")
    print(f"   Content: {content.strip()}")
else:
    print("   ✗ File not found")

# List files created
files = sbx.files.list("/home/user")
print(f"\n📁 Total files in /home/user: {len(files)}")

# Clean up
sbx.kill()
print("\n🛑 Sandbox killed")
