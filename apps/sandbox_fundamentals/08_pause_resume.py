#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Pause and resume sandbox (BETA feature) - saves costs when not in use.
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Creating Sandbox with Auto-Pause ===\n")

# Create sandbox with auto-pause enabled
sbx = Sandbox.beta_create(
    timeout=300,  # 5 minutes
    auto_pause=True
)
sandbox_id = sbx.sandbox_id
print(f"✅ Created sandbox: {sandbox_id}")
print(f"   Auto-pause: enabled")

# Do some work
print("\n📝 Setting up environment...")
sbx.files.write("/home/user/state.txt", "Important state data")
sbx.files.write("/home/user/counter.txt", "0")
print("   Files created")

# Manually pause the sandbox
print("\n⏸️  Pausing sandbox...")
sbx.beta_pause()
print("   Sandbox paused (not consuming resources)")

# Simulate time passing / script ending
time.sleep(2)

print("\n=== Resuming Sandbox ===\n")

# Reconnect - this will automatically resume the paused sandbox
print(f"🔌 Reconnecting to paused sandbox: {sandbox_id}")
sbx_resumed = Sandbox.connect(sandbox_id)
print(f"✅ Sandbox resumed! Running: {sbx_resumed.is_running()}")

# Verify state persisted through pause
print("\n📂 Checking state after resume...")
state = sbx_resumed.files.read("/home/user/state.txt")
print(f"   state.txt: {state}")

counter = sbx_resumed.files.read("/home/user/counter.txt")
print(f"   counter.txt: {counter}")

# Continue working
print("\n🔄 Updating counter...")
current = int(counter.strip())
sbx_resumed.files.write("/home/user/counter.txt", str(current + 1))
new_counter = sbx_resumed.files.read("/home/user/counter.txt")
print(f"   counter.txt: {new_counter}")

# Clean up
print("\n🛑 Cleaning up...")
sbx_resumed.kill()
print("   Sandbox killed")
