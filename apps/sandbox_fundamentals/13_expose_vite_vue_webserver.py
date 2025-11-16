#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Vite + Vue webserver using custom template with Node.js 22 pre-installed.

Uses custom template: agent-sandbox-dev-node22
- Has Node.js 22, bun, uv, Claude Code pre-installed
- Uses npm with Node.js 22 for Vite 7 compatibility
- Fully compatible with Vite 7 (requires Node 20.19+)

Pattern:
1. Create sandbox from custom template
2. Create Vite project with npm + Node 22
3. Start server in background
4. Get public URL with get_host()
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

TEMPLATE_NAME = "agent-sandbox-dev-node22"

print("=== Vite + Vue Webserver (Custom Template) ===\n")

# Create sandbox from custom template with 10-minute timeout
print(f"Creating sandbox from template: {TEMPLATE_NAME}")
sbx = Sandbox.create(template=TEMPLATE_NAME, timeout=600)
print(f"Sandbox: {sbx.sandbox_id}\n")

# Create Vite project with npm (using Node.js 22 from template)
print("Creating Vite project...")
sbx.commands.run(
    "bash -c 'source ~/.nvm/nvm.sh && npm create vite@latest my-app -- --template vue'",
    cwd="/home/user",
    timeout=60
)

# Install dependencies with npm
print("Installing dependencies...")
sbx.commands.run(
    "bash -c 'source ~/.nvm/nvm.sh && npm install'",
    cwd="/home/user/my-app",
    timeout=90
)

# Configure Vite to allow E2B public URLs
vite_config = """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: ['.e2b.app', 'localhost'],
    hmr: {
      clientPort: 443
    }
  }
})
"""
sbx.files.write("/home/user/my-app/vite.config.js", vite_config)

# Start dev server in background with npm (Node.js 22)
print("Starting Vite dev server...\n")
sbx.commands.run(
    "bash -c 'source ~/.nvm/nvm.sh && npm run dev'",
    cwd="/home/user/my-app",
    background=True,
    timeout=0
)

# Wait for server to start
time.sleep(10)

# Get public URL
host = sbx.get_host(5173)
url = f"https://{host}"

print("="*60)
print("✅ VITE SERVER IS LIVE!")
print("="*60)
print(f"\n🌍 URL: {url}\n")
print(f"⏰ Sandbox will auto-kill in 10 minutes")
print(f"📦 Sandbox ID: {sbx.sandbox_id}")
print("="*60)
