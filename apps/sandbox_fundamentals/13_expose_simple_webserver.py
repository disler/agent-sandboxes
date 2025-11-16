#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Simple HTTP server to test E2B port exposure.
"""

import time
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Simple HTTP Server Test ===\n")

# Create sandbox with 10-minute timeout
print("Creating sandbox...")
sbx = Sandbox.create(timeout=600)
print(f"Sandbox ID: {sbx.sandbox_id}\n")

# Create a simple HTML page
print("Creating HTML page...")
html = """<!DOCTYPE html>
<html>
<head>
    <title>E2B Test Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; }
        .success { color: #27ae60; font-size: 24px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 E2B Sandbox Server is LIVE!</h1>
        <p class="success">✅ Success! The server is running and accessible.</p>
        <p>Sandbox ID: """ + sbx.sandbox_id + """</p>
        <p>This page is being served from an E2B sandbox.</p>
    </div>
</body>
</html>"""

sbx.files.write("/home/user/index.html", html)
print("✓ HTML page created\n")

# Start Python HTTP server
print("Starting HTTP server on port 8000...")
server = sbx.commands.run(
    "python3 -m http.server 8000",
    background=True,
    timeout=0
)
print(f"✓ Server started (PID: {server.pid})\n")

# Wait a moment
time.sleep(3)

# Get public URL
host = sbx.get_host(8000)
url = f"https://{host}"

print("="*60)
print("✅ SERVER IS LIVE!")
print("="*60)
print(f"\n🌍 URL: {url}")
print("\n" + "="*60 + "\n")

# Test it
print("Testing server...")
result = sbx.commands.run(f"curl -s {url}", timeout=10)
if "E2B" in result.stdout:
    print("✓ Server responding correctly!\n")
else:
    print("Response:", result.stdout[:200])

print(f"Visit: {url}\n")
print(f"⏰ Sandbox will auto-kill in 10 minutes")
print(f"📦 Sandbox ID: {sbx.sandbox_id}")
