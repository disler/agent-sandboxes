#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Run commands in background and monitor them.
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Create sandbox
sbx = Sandbox.create()
print(f"Sandbox: {sbx.sandbox_id}\n")

# Run a long-running command in background
print("🚀 Starting background command...")
handle = sbx.commands.run(
    "for i in {1..5}; do echo 'Count: '$i; sleep 1; done",
    background=True
)
print(f"   PID: {handle.pid}")
print("   Command is running in background...")

# Wait for it to complete
print("\n⏳ Waiting for command to finish...")
result = handle.wait()

print(f"\n✅ Command completed!")
print(f"   Exit code: {result.exit_code}")
print(f"\n📄 Output:")
print(result.stdout)

# List all running processes
print("📋 All processes:")
processes = sbx.commands.list()
print(f"   Found {len(processes)} processes")

# Clean up
sbx.kill()
