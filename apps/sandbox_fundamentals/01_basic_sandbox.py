#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Basic E2B Sandbox - Create and get info.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Create sandbox
print("Creating sandbox...")
sbx = Sandbox.create()

print(f"✅ Sandbox created: {sbx.sandbox_id}")
print(f"   Running: {sbx.is_running()}")

# Get sandbox info
info = sbx.get_info()
print(f"\n📊 Sandbox Info:")
print(f"   Template: {info.template_id}")
print(f"   Started: {info.started_at}")

# Clean up
sbx.kill()
print("\n🛑 Sandbox killed")
