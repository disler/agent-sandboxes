#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Reuse the same sandbox - connect to existing sandbox by ID.
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Session 1: Create and Setup Sandbox ===\n")

# Create sandbox
sbx = Sandbox.create()
sandbox_id = sbx.sandbox_id
print(f"✅ Created sandbox: {sandbox_id}")

# Do some work - create files
print("\n📝 Setting up sandbox...")
sbx.files.write("/home/user/persistent.txt", "This data persists!")
sbx.commands.run("mkdir -p /home/user/myproject")
sbx.files.write("/home/user/myproject/config.json", '{"env": "production"}')
sbx.files.write("/home/user/myproject/app.py", 'print("Hello from persistent app")')
print("   Created files in sandbox")

# Run a command to verify
result = sbx.commands.run("python3 /home/user/myproject/app.py")
print(f"   Test run: {result.stdout.strip()}")

# Keep sandbox alive but "disconnect" (in real scenario, this could be end of script)
print(f"💾 Sandbox ID saved: {sandbox_id}")
print("   (Sandbox still running, keeping it alive for reconnection...)\n")

# Simulate disconnection by creating new variable
# In real use, you'd save sandbox_id to a file/DB and use it later
sbx_original = sbx

print("=== Session 2: Reconnect to Same Sandbox ===\n")
time.sleep(2)

# Reconnect to the same sandbox
print(f"🔌 Reconnecting to sandbox: {sandbox_id}")
sbx_reconnected = Sandbox.connect(sandbox_id)
print(f"✅ Reconnected! Running: {sbx_reconnected.is_running()}")

# Verify our files are still there
print("\n📂 Checking persistent data...")
content = sbx_reconnected.files.read("/home/user/persistent.txt")
print(f"   persistent.txt: {content}")

config = sbx_reconnected.files.read("/home/user/myproject/config.json")
print(f"   config.json: {config}")

# Verify app still works
print("\n🐍 Testing persistent app...")
result = sbx_reconnected.commands.run("python3 /home/user/myproject/app.py")
print(f"   Output: {result.stdout.strip()}")

# Do more work in the same sandbox
print("📝 Continuing work in same sandbox...")
sbx_reconnected.files.write("/home/user/session2.txt", "Added in session 2")
files = sbx_reconnected.files.list("/home/user")
print(f"   Files in /home/user: {len(files)} files")

# Clean up
print("\n🛑 Cleaning up...")
sbx_reconnected.kill()
print("   Sandbox killed")
