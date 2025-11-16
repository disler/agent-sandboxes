#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Environment variables in sandbox.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Create sandbox with custom environment variables
print("Creating sandbox with custom env vars...\n")
sbx = Sandbox.create(
    envs={
        "MY_VAR": "hello",
        "API_KEY": "secret123",
        "DEBUG": "true"
    }
)
print(f"Sandbox: {sbx.sandbox_id}\n")

# Access env vars in commands
print("🔑 Checking environment variables:")
result = sbx.commands.run("echo $MY_VAR")
print(f"   MY_VAR: {result.stdout.strip()}")

result = sbx.commands.run("echo $API_KEY")
print(f"   API_KEY: {result.stdout.strip()}")

result = sbx.commands.run("echo $DEBUG")
print(f"   DEBUG: {result.stdout.strip()}")

# Pass additional env vars to specific command
print("\n🔑 Command-specific env vars:")
result = sbx.commands.run(
    "echo $TEMP_VAR",
    envs={"TEMP_VAR": "temporary"}
)
print(f"   TEMP_VAR: {result.stdout.strip()}")

# Verify TEMP_VAR doesn't persist
result = sbx.commands.run("echo $TEMP_VAR")
print(f"   TEMP_VAR (after): {result.stdout.strip() or '(empty)'}")

# Use env vars in Python
print("\n🐍 Using env vars in Python:")
result = sbx.commands.run(
    "python3 -c 'import os; print(os.getenv(\"MY_VAR\"))'"
)
print(f"   Python sees MY_VAR: {result.stdout.strip()}")

# Clean up
sbx.kill()
