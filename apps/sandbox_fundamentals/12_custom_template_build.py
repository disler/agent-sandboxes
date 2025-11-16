#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Build custom template - create a template with Node.js 22, npm, uv, and Claude Code pre-installed.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from e2b import Template

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

TEMPLATE_NAME = "agent-sandbox-dev-node22"

print("=== Building Custom Template ===\n")

# Define the template with pre-installed tools
print("📝 Defining template...")
template = (
    Template()
    .from_base_image()
    # Install nvm
    .run_cmd("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash")
    # Install Node 22 via nvm
    .run_cmd("bash -c 'export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm install 22'")
    # Remove old Node.js from base image (requires sudo)
    .run_cmd("sudo rm -f /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx")
    # Create symlinks to nvm's Node 22 (makes it the default, requires sudo)
    .run_cmd("bash -c 'export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm use 22 && sudo ln -s $(which node) /usr/local/bin/node && sudo ln -s $(which npm) /usr/local/bin/npm && sudo ln -s $(which npx) /usr/local/bin/npx'")
    # Install uv
    .run_cmd("curl -LsSf https://astral.sh/uv/install.sh | sh")
)
print(f"   ✓ Template defined: {TEMPLATE_NAME}")
print("   Tools to be installed: Node.js 22 (via nvm + symlinks), npm, npx, uv")

# Build the template
print(f"\n🏗️  Building template '{TEMPLATE_NAME}'...")
print("   (This may take a few minutes...)\n")

try:
    Template.build(
        template,
        alias=TEMPLATE_NAME,
        cpu_count=2,
        memory_mb=1024,
    )
    print(f"   ✅ Template built successfully: {TEMPLATE_NAME}")
    print(f"\n💡 Use this template with:")
    print(f"   Sandbox.create('{TEMPLATE_NAME}')")
except Exception as e:
    print(f"   ❌ Build failed: {e}")
    print("\n   Note: Template building might require CLI or different API")
