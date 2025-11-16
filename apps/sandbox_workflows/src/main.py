"""
Main CLI entry point for obox (sandbox workflows).
"""

from pathlib import Path
import typer
from rich.console import Console
from dotenv import load_dotenv

# Load .env from project root
# starts at: apps/sandbox_workflows/src/main.py
# .parent: apps/sandbox_workflows/src/
# .parent.parent: apps/sandbox_workflows/
# .parent.parent.parent: apps/
# .parent.parent.parent.parent: root
root_dir = Path(__file__).parent.parent.parent.parent
load_dotenv(root_dir / ".env")

# Initialize Typer app
app = typer.Typer(
    name="obox",
    help="Orchestrated Sandbox Workflows - Multi-agent experimentation with E2B sandboxes",
    add_completion=False,
)

# Initialize Rich console for pretty output
console = Console()

# Import and register commands
try:
    from .commands.sandbox_fork import sandbox_fork_command

    app.command(name="sandbox-fork")(sandbox_fork_command)
except ImportError as e:
    console.print(f"[red]Error importing commands: {e}[/red]")


if __name__ == "__main__":
    app()
