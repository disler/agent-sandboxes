#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Run shell commands in sandbox.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Create sandbox
sbx = Sandbox.create()
print(f"Sandbox: {sbx.sandbox_id}\n")

# Run a simple command
print("💻 Running: uname -a")
result = sbx.commands.run("uname -a")
print(f"   {result.stdout.strip()}")

# Run command with output
print("\n💻 Running: echo 'Hello from sandbox'")
result = sbx.commands.run("echo 'Hello from sandbox'")
print(f"   {result.stdout.strip()}")

# Run command that creates a file
print("\n💻 Creating file via command...")
sbx.commands.run("echo 'Created by command' > /tmp/cmd_output.txt")
content = sbx.files.read("/tmp/cmd_output.txt")
print(f"   File content: {content.strip()}")

# Run command in specific directory
print("\n💻 Running: pwd in /home/user")
result = sbx.commands.run("pwd", cwd="/home/user")
print(f"   Working dir: {result.stdout.strip()}")

# Run Python command
print("\n💻 Running Python...")
result = sbx.commands.run("python3 -c 'print(2 + 2)'")
print(f"   Result: {result.stdout.strip()}")

# Clean up
sbx.kill()
