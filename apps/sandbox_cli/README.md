# E2B Sandbox CLI

A streamlined command-line interface for managing E2B sandboxes with a powerful unified command execution interface.

## Installation

```bash
# Install dependencies
uv sync

# Run the CLI
uv run sbx --help
```

## Quick Start

### 1. Initialize a New Sandbox

```bash
# Create a new sandbox and save the ID
uv run sbx init

# Set the sandbox ID as an environment variable
export SANDBOX_ID=$(cat .sandbox_id)

# Create with a custom template
uv run sbx init --template claude-code --timeout 900

# Create with environment variables
uv run sbx init --env API_KEY=secret --env DEBUG=true
```

### 2. File Operations

```bash
# List files in root directory
uv run sbx files ls $SANDBOX_ID /

# List files with depth
uv run sbx files ls $SANDBOX_ID /home/user --depth 2

# Write a file (text)
uv run sbx files write $SANDBOX_ID /home/user/test.txt "Hello World"

# Read a file (text)
uv run sbx files read $SANDBOX_ID /home/user/test.txt

# Upload a file (binary support - images, PDFs, executables, etc.)
uv run sbx files upload $SANDBOX_ID /path/to/local/image.png /home/user/image.png

# Download a file (binary support)
uv run sbx files download $SANDBOX_ID /home/user/output.pdf /path/to/local/output.pdf

# Check if file exists
uv run sbx files exists $SANDBOX_ID /home/user/test.txt

# Get file info
uv run sbx files info $SANDBOX_ID /home/user/test.txt

# Create directory
uv run sbx files mkdir $SANDBOX_ID /home/user/mydir

# Remove file
uv run sbx files rm $SANDBOX_ID /home/user/test.txt

# Rename/move file
uv run sbx files mv $SANDBOX_ID /home/user/old.txt /home/user/new.txt
```

### 3. Command Execution (Unified Interface)

The `exec` command is the most powerful feature - it replaces all specialized commands with a single flexible interface.

```bash
# Basic execution
uv run sbx exec $SANDBOX_ID "python --version"

# Run with environment variables
uv run sbx exec $SANDBOX_ID "echo \$MY_VAR" --env MY_VAR=value

# Run in specific directory
uv run sbx exec $SANDBOX_ID "pwd" --cwd /home/user/project

# Run as root
uv run sbx exec $SANDBOX_ID "apt-get update" --root

# Shell features (pipes, redirections, wildcards)
uv run sbx exec $SANDBOX_ID "ps aux | grep python" --shell

# Background execution
uv run sbx exec $SANDBOX_ID "sleep 10 && echo done" --background

# Custom timeout
uv run sbx exec $SANDBOX_ID "long-running-command" --timeout 300

# Combine flags
uv run sbx exec $SANDBOX_ID "echo \$VAR > output.txt" --shell --env VAR=hello --cwd /home/user
```

### 4. Package Management (via exec)

Instead of specialized commands, use `exec` with package managers:

```bash
# Install uv (Python package manager)
uv run sbx exec $SANDBOX_ID "curl -LsSf https://astral.sh/uv/install.sh | sh" --shell --timeout 120

# Install Python packages
uv run sbx exec $SANDBOX_ID "/home/user/.local/bin/uv pip install --system requests pydantic"

# List Python packages
uv run sbx exec $SANDBOX_ID "/home/user/.local/bin/uv pip list"

# Install bun (JavaScript runtime)
uv run sbx exec $SANDBOX_ID "curl -fsSL https://bun.sh/install | bash" --shell --timeout 120

# Install Node packages
uv run sbx exec $SANDBOX_ID "/home/user/.bun/bin/bun add cowsay"

# List Node packages
uv run sbx exec $SANDBOX_ID "/home/user/.bun/bin/bun pm ls"
```

### 5. Git Operations (via exec)

Use `exec` with the `--cwd` flag for git operations:

```bash
# Clone a repository
uv run sbx exec $SANDBOX_ID "git clone https://github.com/user/repo /home/user/repo"

# Configure git user
uv run sbx exec $SANDBOX_ID "git config --global user.email 'user@example.com'" --shell
uv run sbx exec $SANDBOX_ID "git config --global user.name 'User Name'" --shell

# Check status
uv run sbx exec $SANDBOX_ID "git status" --cwd /home/user/repo

# Stage files
uv run sbx exec $SANDBOX_ID "git add ." --cwd /home/user/repo

# Commit changes
uv run sbx exec $SANDBOX_ID "git commit -m 'Update files'" --cwd /home/user/repo

# View log
uv run sbx exec $SANDBOX_ID "git log --oneline -n 5" --cwd /home/user/repo

# Pull changes
uv run sbx exec $SANDBOX_ID "git pull origin main" --cwd /home/user/repo

# Push changes
uv run sbx exec $SANDBOX_ID "git push origin main" --cwd /home/user/repo
```

### 6. Sandbox Management

```bash
# Create a new sandbox
uv run sbx sandbox create --template base --timeout 600

# Create sandbox with custom environment
uv run sbx sandbox create --env API_KEY=secret --env DEBUG=true

# Create sandbox with auto-pause (beta)
uv run sbx sandbox create --auto-pause

# Connect to existing sandbox
uv run sbx sandbox connect <sandbox_id>

# Get sandbox information
uv run sbx sandbox info $SANDBOX_ID

# Check if sandbox is running
uv run sbx sandbox status $SANDBOX_ID

# Pause sandbox (beta)
uv run sbx sandbox pause $SANDBOX_ID

# Kill sandbox
uv run sbx sandbox kill $SANDBOX_ID
```

## Command Structure

The CLI is organized into **three core command groups**:

- **`sbx init`** - Quick sandbox initialization with template support
- **`sbx sandbox`** - Sandbox lifecycle management (create, connect, kill, pause, info, status)
- **`sbx files`** - File system operations using E2B SDK APIs (ls, read, write, upload, download, rm, mkdir, mv, exists, info)
- **`sbx exec`** - Unified command execution with full control (all flags: --cwd, --user, --root, --shell, --env, --timeout, --background, --stdin)

## Architecture

```
apps/sandbox_cli/
   src/
      main.py              # Main CLI entry point
      commands/            # CLI commands (one file per command group)
         sandbox.py       # Sandbox lifecycle management
         files.py         # File operations using SDK APIs
         exec.py          # Unified command execution
      modules/             # Reusable logic modules
          sandbox.py       # Sandbox connection management
          files.py         # File operation helpers
          commands.py      # Command execution helpers
   pyproject.toml           # Project configuration
   README.md
```

## Key Design Principles

### 1. Unified Command Execution

Instead of having specialized command groups for packages, git, and general commands, we use a single powerful `exec` command that supports:
- Shell features (`--shell` for pipes, redirections, wildcards)
- Working directory (`--cwd`)
- User privileges (`--root` or `--user`)
- Environment variables (`--env`)
- Background execution (`--background`)
- Custom timeouts (`--timeout`)

**Benefits:**
- **80% less code** - Fewer commands to maintain
- **More flexible** - Run ANY command, not just pre-defined ones
- **Agent-friendly** - One interface to learn instead of dozens
- **Composable** - Combine flags for complex operations

### 2. SDK-Based File Operations

File operations use E2B's SDK APIs instead of shell commands for:
- **Reliability** - Structured responses, better error handling
- **Performance** - Direct API calls vs. command execution
- **Type safety** - Returns proper objects with metadata
- **Binary support** - Upload/download any file type (images, PDFs, executables, etc.)

## Features

- **Sandbox Management**: Create, connect, pause, resume, and kill sandboxes
- **File Operations**: Complete filesystem control with SDK APIs
  - Text file read/write
  - Binary file upload/download (images, PDFs, executables, etc.)
  - Directory operations (list, create, remove, rename)
- **Unified Command Execution**: Run ANY command with full control
- **Environment Variables**: Custom environment configuration
- **Templates**: Support for custom sandbox templates
- **Rich Output**: Beautiful terminal output with tables and colors

## Usage Tips

1. **Save Sandbox ID**: Always export your sandbox ID for easy reuse:
   ```bash
   export SANDBOX_ID=$(cat .sandbox_id)
   ```

2. **Use Shell Flag**: For pipes, redirections, and wildcards, use `--shell`:
   ```bash
   uv run sbx exec $SANDBOX_ID "cat file.txt | grep pattern" --shell
   ```

3. **Working Directory**: Use `--cwd` instead of `cd`:
   ```bash
   uv run sbx exec $SANDBOX_ID "git status" --cwd /home/user/repo
   ```

4. **Root Privileges**: Use `--root` for system operations:
   ```bash
   uv run sbx exec $SANDBOX_ID "apt-get install nginx" --root --timeout 300
   ```

5. **Keep Sandbox Alive**: Increase timeout for long-running operations:
   ```bash
   uv run sbx init --timeout 3600  # 1 hour
   ```

6. **Binary Files**: Use upload/download for binary files (images, PDFs, executables):
   ```bash
   # Upload an image
   uv run sbx files upload $SANDBOX_ID ./local_image.png /home/user/image.png

   # Download generated PDF
   uv run sbx files download $SANDBOX_ID /home/user/report.pdf ./report.pdf
   ```

## Agent Integration

This CLI is designed to be wrapped and given to AI agents for full sandbox control. The unified `exec` command provides:

- **Predictable interface** - One command signature instead of many
- **Maximum flexibility** - Agents can run ANY shell command
- **Composable operations** - Combine flags for complex scenarios
- **Error handling** - Clear exit codes and error messages

Agents can:
- Create isolated environments
- Install any packages and dependencies
- Run code and commands with full control
- Manage files with structured APIs
- All with a simple, consistent interface

## Examples

### Example 1: Python Development Workflow

```bash
# Initialize sandbox
uv run sbx init --timeout 900
export SANDBOX_ID=$(cat .sandbox_id)

# Install uv package manager
uv run sbx exec $SANDBOX_ID "curl -LsSf https://astral.sh/uv/install.sh | sh" --shell --timeout 120

# Install Python packages
uv run sbx exec $SANDBOX_ID "/home/user/.local/bin/uv pip install --system requests beautifulsoup4"

# Create a script using files API
uv run sbx files write $SANDBOX_ID /home/user/scraper.py "
import requests
from bs4 import BeautifulSoup

response = requests.get('https://example.com')
soup = BeautifulSoup(response.content, 'html.parser')
print(soup.title.string)
"

# Run the script
uv run sbx exec $SANDBOX_ID "python3 /home/user/scraper.py"

# Clean up
uv run sbx sandbox kill $SANDBOX_ID
```

### Example 2: Git Workflow

```bash
# Initialize and setup
uv run sbx init
export SANDBOX_ID=$(cat .sandbox_id)

# Configure git
uv run sbx exec $SANDBOX_ID "git config --global user.email 'dev@example.com' && git config --global user.name 'Developer'" --shell

# Clone repo
uv run sbx exec $SANDBOX_ID "git clone https://github.com/user/repo /home/user/repo"

# Make changes using files API
uv run sbx files write $SANDBOX_ID /home/user/repo/README.md "# Updated"

# Commit changes
uv run sbx exec $SANDBOX_ID "git add . && git commit -m 'Update README'" --shell --cwd /home/user/repo

# View history
uv run sbx exec $SANDBOX_ID "git log --oneline -n 5" --cwd /home/user/repo

# Clean up
uv run sbx sandbox kill $SANDBOX_ID
```

### Example 3: Complex Multi-Step Operation

```bash
# Initialize with template
uv run sbx init --template claude-code --env PROJECT=myapp
export SANDBOX_ID=$(cat .sandbox_id)

# Create project structure
uv run sbx files mkdir $SANDBOX_ID /home/user/myapp
uv run sbx files mkdir $SANDBOX_ID /home/user/myapp/src

# Install dependencies and run tests (combined operation)
uv run sbx exec $SANDBOX_ID "
  cd /home/user/myapp &&
  python -m venv venv &&
  source venv/bin/activate &&
  pip install pytest &&
  pytest --version
" --shell --timeout 300

# Background task
uv run sbx exec $SANDBOX_ID "python server.py" --background --cwd /home/user/myapp

# Clean up
uv run sbx sandbox kill $SANDBOX_ID
```

### Example 4: Working with Binary Files (Images, PDFs, etc.)

```bash
# Initialize sandbox
uv run sbx init
export SANDBOX_ID=$(cat .sandbox_id)

# Upload an image for processing
uv run sbx files upload $SANDBOX_ID ./input_photo.jpg /home/user/input.jpg

# Install image processing library
uv run sbx exec $SANDBOX_ID "curl -LsSf https://astral.sh/uv/install.sh | sh" --shell --timeout 120
uv run sbx exec $SANDBOX_ID "/home/user/.local/bin/uv pip install --system pillow"

# Process the image (resize, convert format, etc.)
uv run sbx files write $SANDBOX_ID /home/user/process_image.py "
from PIL import Image

# Open and resize image
img = Image.open('/home/user/input.jpg')
img_resized = img.resize((800, 600))
img_resized.save('/home/user/output.png', 'PNG')
print('Image processed successfully')
"

# Run the processing script
uv run sbx exec $SANDBOX_ID "python3 /home/user/process_image.py"

# Download the processed image
uv run sbx files download $SANDBOX_ID /home/user/output.png ./output.png

# Verify the file
ls -lh ./output.png

# Clean up
uv run sbx sandbox kill $SANDBOX_ID
```

## Comparison: Before vs After

### Before (Specialized Commands):
```bash
# Multiple command groups, each with specific syntax
sbx cmd run $ID "echo hello"
sbx packages install-uv $ID
sbx packages uv $ID --system requests
sbx git clone $ID https://... /path
sbx git status $ID /path
```

### After (Unified Interface):
```bash
# One powerful command with composable flags
sbx exec $ID "echo hello"
sbx exec $ID "curl ... | sh" --shell --timeout 120
sbx exec $ID "uv pip install --system requests"
sbx exec $ID "git clone https://... /path"
sbx exec $ID "git status" --cwd /path
```

**Result:** Fewer concepts to learn, more flexibility, agent-friendly interface.

## Requirements

- Python >= 3.12
- UV package manager
- E2B API key (set in .env file)

## Development

Built with:
- **Click**: Command-line interface framework
- **Rich**: Beautiful terminal output
- **E2B SDK**: Sandbox management
- **UV**: Fast Python package management

## License

Part of the agent-sandboxes project.
