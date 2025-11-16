#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
File operations - write, read, check exists.
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

# Write a file
print("📝 Writing file...")
sbx.files.write("/tmp/hello.txt", "Hello from E2B sandbox!")
print("   Created: /tmp/hello.txt")

# Check if file exists
exists = sbx.files.exists("/tmp/hello.txt")
print(f"   Exists: {exists}")

# Read the file
print("\n📖 Reading file...")
content = sbx.files.read("/tmp/hello.txt")
print(f"   Content: {content}")

# Get file info
info = sbx.files.get_info("/tmp/hello.txt")
print(f"\n📊 File info:")
print(f"   Size: {info.size} bytes")
print(f"   Permissions: {info.permissions}")

# Create a directory and write multiple files
print("\n📁 Creating directory with files...")
sbx.files.make_dir("/tmp/test_dir")
sbx.files.write("/tmp/test_dir/file1.txt", "Content 1")
sbx.files.write("/tmp/test_dir/file2.txt", "Content 2")

files = sbx.files.list("/tmp/test_dir")
print(f"   Created {len(files)} files in /tmp/test_dir")

# Clean up
sbx.kill()
