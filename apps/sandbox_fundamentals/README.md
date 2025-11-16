# E2B Sandbox Fundamentals

Practical examples demonstrating core E2B SDK patterns and capabilities.

## Setup

1. **Install uv** (Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set E2B API Key**:
   In the root run cp `.env.sample` to `.env` and fill in your API key:
   ```
   E2B_API_KEY=your_api_key_here
   ```

3. **Run any example**:
   ```bash
   uv run 01_basic_sandbox.py
   ```

## Examples

### Basic Operations
- **01_basic_sandbox.py** - Create sandbox, run command, get output
- **01_basic_sandbox_keep_alive.py** - Create sandbox that stays alive until timeout (for testing)
- **02_list_files.py** - List files and directories with metadata
- **03_file_operations.py** - Read, write, upload, download files
- **04_run_commands.py** - Execute commands with various options (cwd, timeout, user)

### Advanced Features
- **05_environment_vars.py** - Pass environment variables to sandbox
- **06_background_commands.py** - Run long-running processes in background
- **07_reuse_sandbox.py** - Connect to existing sandbox by ID
- **08_pause_resume.py** - Pause and resume sandboxes (beta feature)

### Development Workflows
- **09_claude_code_agent.py** - Run Claude Code AI agent in sandbox
- **10_install_packages.py** - Install and use Python/npm packages
- **11_git_operations.py** - Clone repos and run git commands

### Custom Templates
- **12_custom_template_build.py** - Build custom template with pre-installed tools
- **12_custom_template_reuse.py** - Reuse custom template for faster startup

### Port Exposure
- **13_expose_simple_webserver.py** - Simple Python HTTP server with public URL
- **13_expose_vite_vue_webserver.py** - Vite + Vue dev server with public URL (requires Node.js 22)

## Documentation

See `../../ai_docs/README.md` for complete E2B API reference.
