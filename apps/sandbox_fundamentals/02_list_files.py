#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
List files in sandbox filesystem.
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

# List files in root
print("=== Files in / ===")
files = sbx.files.list("/")
for f in files:
    type_icon = "📁" if f.type.value == "dir" else "📄"
    print(f"{type_icon} {f.name:<20} {f.permissions:<12} {f.size:>10}")

# List files in /home recursively
print("\n=== Files in /home (depth=2) ===")
home_files = sbx.files.list("/home", depth=2)
for f in home_files:
    type_icon = "📁" if f.type.value == "dir" else "📄"
    indent = "  " * (f.path.count('/') - 1)
    print(f"{indent}{type_icon} {f.name}")

# Clean up
sbx.kill()
