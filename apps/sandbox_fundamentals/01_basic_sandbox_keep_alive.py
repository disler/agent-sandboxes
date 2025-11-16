#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Basic sandbox keep-alive example.

Creates a sandbox and keeps it alive until natural timeout.
Useful for testing sandbox listing and connection features.

Pattern:
1. Create sandbox with custom timeout
2. Print sandbox ID for reference
3. Let it run until natural timeout (no manual kill)
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Basic Sandbox Keep-Alive ===\n")

# Create sandbox with 5-minute timeout
print("Creating sandbox with 5-minute timeout...")
sbx = Sandbox.create(template="base", timeout=300)

print(f"✓ Sandbox created: {sbx.sandbox_id}\n")
print(f"📦 Sandbox ID: {sbx.sandbox_id}")
print(f"⏰ Timeout: 5 minutes (300 seconds)")
print(f"🔍 Test listing: sbx sandbox list")
print(f"🔌 Test connect: sbx sandbox connect {sbx.sandbox_id}")
print(f"\n⏳ Sandbox will remain alive until natural timeout...")
print(f"   (Script will exit but sandbox continues running)\n")

# Keep script alive for a bit to show it's running
print("Waiting 10 seconds before exiting script...")
time.sleep(10)

print("\n✅ Script complete - sandbox still running!")
print(f"   Sandbox will auto-kill after 5 minutes")
print(f"   Test list command: cd apps/sandbox_cli && uv run sbx sandbox list")
