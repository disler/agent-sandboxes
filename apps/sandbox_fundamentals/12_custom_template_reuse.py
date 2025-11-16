#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Reuse custom template - create sandbox from pre-built template with uv, bun, and claude code.
"""

from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

TEMPLATE_NAME = "agent-sandbox-dev-node22"

print("=== Using Custom Template ===\n")

# Create sandbox from template
print(f"🚀 Creating sandbox from template '{TEMPLATE_NAME}'...")

try:
    sbx = Sandbox.create(TEMPLATE_NAME)
    print(f"   ✅ Sandbox created: {sbx.sandbox_id}")

    # Verify tools are available
    print("\n🔍 Verifying pre-installed tools...")

    # Check uv
    result = sbx.commands.run("~/.local/bin/uv --version || echo 'uv not found'")
    if "uv not found" not in result.stdout:
        print(f"   ✓ uv: {result.stdout.strip()}")
    else:
        print(f"   ✗ uv not found")

    # Check bun
    result = sbx.commands.run("~/.bun/bin/bun --version || echo 'bun not found'")
    if "bun not found" not in result.stdout:
        print(f"   ✓ bun: {result.stdout.strip()}")
    else:
        print(f"   ✗ bun not found")

    # Check claude
    result = sbx.commands.run("claude --version || echo 'claude not found'")
    if "claude not found" not in result.stdout:
        print(f"   ✓ claude: {result.stdout.strip()}")
    else:
        print(f"   ✗ claude not found")

    # Demonstrate using the tools
    print("\n🎯 Using pre-installed tools...")

    # Use uv to install a package quickly
    print("   Installing httpx with uv...")
    result = sbx.commands.run("~/.local/bin/uv pip install --system httpx", timeout=60)
    print(f"   ✓ Package installed")

    # Verify the package works
    result = sbx.commands.run(
        "python3 -c 'import httpx; print(f\"httpx {httpx.__version__}\")'"
    )
    print(f"   ✓ {result.stdout.strip()}")

    # Use bun to run a simple script
    print("\n   Running JavaScript with bun...")
    sbx.files.write("/home/user/test.js", "console.log('Bun works! 🥟')")
    result = sbx.commands.run("~/.bun/bin/bun /home/user/test.js")
    print(f"   ✓ {result.stdout.strip()}")

    print(f"\n📌 Template '{TEMPLATE_NAME}' successfully reused!")
    print("   Benefits:")
    print("   - Zero installation time (tools pre-installed)")
    print("   - Consistent environment across all sandboxes")
    print("   - Fast sandbox creation")

    sbx.kill()
    print("\n🛑 Sandbox killed")

except Exception as e:
    print(f"   ❌ Could not create sandbox: {e}")
    print(f"\n   Template '{TEMPLATE_NAME}' may not exist yet.")
    print(f"   Build it first with: ./12_custom_template_build.py")
