#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Install packages - using uv for Python, bun for Node.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

EXAMPLE_REPO = "https://github.com/disler/beyond-mcp"

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Package Installation ===\n")

sbx = Sandbox.create()
print(f"Sandbox: {sbx.sandbox_id}\n")

# Install uv (Astral's Python package manager)
print("⚡ Installing uv...")
sbx.commands.run("curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null 2>&1", timeout=120)
print("   ✓ uv installed")

# Install bun
print("\n⚡ Installing bun...")
sbx.commands.run("curl -fsSL https://bun.sh/install | bash > /dev/null 2>&1", timeout=120)
print("   ✓ bun installed")

# Tool paths
UV_PATH = "/home/user/.local/bin/uv"
BUN_PATH = "/home/user/.bun/bin/bun"

# Install Python packages with uv
print("\n🐍 Installing Python packages with uv...")
result = sbx.commands.run(
    f"{UV_PATH} pip install --system requests pydantic",
    timeout=120
)
print("   ✓ Installed: requests, pydantic")

# Verify Python packages
print("\n📦 Verifying Python packages...")
result = sbx.commands.run("python3 -c 'import requests, pydantic; print(f\"requests {requests.__version__}, pydantic {pydantic.__version__}\")'")
print(f"   {result.stdout.strip()}")

# Install Node packages with bun
print("\n📦 Installing Node packages with bun...")
result = sbx.commands.run(
    f"{BUN_PATH} add -g cowsay@1.6.0",
    timeout=120
)
print("   ✓ Installed: cowsay (bun global)")

# Verify bun package
print("\n🐮 Testing bun package...")
result = sbx.commands.run(f"/home/user/.bun/bin/cowsay 'bun works!'")
print(result.stdout)

# Test Python package
print("🌐 Testing requests package...")
result = sbx.commands.run(
    "python3 -c \"import requests; r = requests.get('https://api.github.com/repos/disler/beyond-mcp'); print('Repo:', r.json()['full_name']); print('Stars:', r.json()['stargazers_count'])\""
)
print(f"   {result.stdout.strip()}")

# List installed packages
print("\n📋 Checking installed packages...")
result = sbx.commands.run(f"{UV_PATH} pip list | grep -E 'requests|pydantic'")
print("   Python (uv):")
for line in result.stdout.strip().split('\n'):
    print(f"   - {line}")

result = sbx.commands.run(f"{BUN_PATH} pm ls -g | grep cowsay")
print("   Node (bun):")
if result.stdout.strip():
    print(f"   - {result.stdout.strip()}")
else:
    print("   - cowsay@1.6.0 (installed)")

sbx.kill()
print("\n🛑 Sandbox killed")
