#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Git operations - clone repo, make changes, commit, view log.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

EXAMPLE_REPO = "https://github.com/disler/beyond-mcp"

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Git Operations ===\n")

sbx = Sandbox.create()
print(f"Sandbox: {sbx.sandbox_id}\n")

# Clone the repository
print(f"📥 Cloning {EXAMPLE_REPO}...")
result = sbx.commands.run(
    f"git clone {EXAMPLE_REPO} /home/user/beyond-mcp",
    timeout=60
)
print("   ✓ Repository cloned")

# Check what we have
print("\n📂 Repository contents:")
result = sbx.commands.run("ls -la /home/user/beyond-mcp")
files = sbx.files.list("/home/user/beyond-mcp")
for f in files:
    type_icon = "📁" if f.type.value == "dir" else "📄"
    print(f"   {type_icon} {f.name}")

# Make a random change
print("✏️  Making a random change...")
sbx.files.write(
    "/home/user/beyond-mcp/test_change.txt",
    "This is a test change made in the sandbox!"
)
print("   ✓ Created test_change.txt")

# Git status before commit
print("\n📊 Git status before commit:")
result = sbx.commands.run(
    "cd /home/user/beyond-mcp && git status --short"
)
print(result.stdout)

# Configure git user
print("⚙️  Configuring git user...")
sbx.commands.run("git config --global user.email 'sandbox@e2b.dev'")
sbx.commands.run("git config --global user.name 'E2B Sandbox'")
print("   ✓ Git user configured")

# Stage and commit the change
print("\n💾 Staging and committing change...")
sbx.commands.run("cd /home/user/beyond-mcp && git add test_change.txt")
result = sbx.commands.run(
    "cd /home/user/beyond-mcp && git commit -m 'Test change from E2B sandbox'"
)
print(result.stdout)

# Git log to show the commit
print("\n📜 Git log (last 3 commits):")
result = sbx.commands.run(
    "cd /home/user/beyond-mcp && git log --oneline -n 3"
)
print(result.stdout)

# Show detailed info about our commit
print("🔍 Detailed commit info:")
result = sbx.commands.run(
    "cd /home/user/beyond-mcp && git log -1 --stat"
)
print(result.stdout)

# Verify the change is committed
print("✅ Final git status:")
result = sbx.commands.run(
    "cd /home/user/beyond-mcp && git status"
)
print(result.stdout)

sbx.kill()
print("\n🛑 Sandbox killed")
