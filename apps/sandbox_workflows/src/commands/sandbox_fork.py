"""
Sandbox fork command implementation.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional
import subprocess
import sys

from ..modules import (
    constants,
    logs,
    forks,
    git_utils,
)

console = Console()


def log_and_print(log_manager, message: str, style: str = ""):
    """
    Helper to both print to console and log to primary logger.

    Args:
        log_manager: LogManager instance
        message: Plain text message
        style: Rich-formatted string for console (optional)
    """
    # Print to console with style
    if style:
        console.print(style)
    else:
        console.print(message)

    # Log plain text (strip Rich markup for log file)
    import re
    plain_text = re.sub(r'\[/?[^\]]+\]', '', message if not style else style)
    log_manager.log_primary(plain_text)


def sandbox_fork_command(
    repo_url: str = typer.Argument(..., help="Git repository URL to clone"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Git branch to checkout"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt text or path to prompt file"),
    num_forks: int = typer.Option(constants.DEFAULT_FORKS, "--forks", "-f", help="Number of forks to create"),
    max_turns: Optional[int] = typer.Option(None, "--max-turns", "-t", help="Maximum number of conversation turns (default: from constants)"),
    model: str = typer.Option("sonnet", "--model", "-m", help="Claude model to use: opus, sonnet, or haiku (default: sonnet)"),
):
    """
    Fork a git repository into multiple sandboxes and run agents in parallel.

    Creates N isolated E2B sandboxes, clones the repository into each,
    and runs a Claude Code agent with the given prompt. All execution
    is logged to separate files and displayed in VSCode.
    """
    # === SETUP ===
    # Parse repository name from URL early for logging
    repo_name = git_utils.parse_repo_name(repo_url)

    # Create LogManager FIRST so we can log everything
    log_manager = logs.LogManager(repo_name)

    # === VALIDATION ===
    log_and_print(log_manager, "\n[bold cyan]Sandbox Fork - Multi-Agent Experimentation[/bold cyan]\n", "\n[bold cyan]Sandbox Fork - Multi-Agent Experimentation[/bold cyan]\n")

    # Validate repo URL format
    if not git_utils.validate_git_url(repo_url):
        log_and_print(log_manager, f"[red]Error: Invalid git repository URL: {repo_url}[/red]", f"[red]Error: Invalid git repository URL: {repo_url}[/red]")
        log_and_print(log_manager, "[yellow]Expected format: https://github.com/user/repo or git@github.com:user/repo[/yellow]", "[yellow]Expected format: https://github.com/user/repo or git@github.com:user/repo[/yellow]")
        log_manager.close_all()
        raise typer.Exit(1)

    # Validate fork count
    if num_forks < 1 or num_forks > constants.MAX_FORKS:
        log_and_print(log_manager, f"[red]Error: Fork count must be between 1 and {constants.MAX_FORKS}[/red]", f"[red]Error: Fork count must be between 1 and {constants.MAX_FORKS}[/red]")
        log_manager.close_all()
        raise typer.Exit(1)

    # Generate branch name if not provided
    if not branch:
        branch = git_utils.generate_branch_name()
        log_and_print(log_manager, f"[yellow]No branch specified, using default branch or generating: {branch}[/yellow]", f"[yellow]No branch specified, using default branch or generating: {branch}[/yellow]")
    else:
        # Validate branch name
        if not git_utils.validate_branch_name(branch):
            log_and_print(log_manager, f"[red]Error: Invalid branch name: {branch}[/red]", f"[red]Error: Invalid branch name: {branch}[/red]")
            log_and_print(log_manager, "[yellow]Branch names must contain only alphanumeric, dash, underscore, slash, and dot[/yellow]", "[yellow]Branch names must contain only alphanumeric, dash, underscore, slash, and dot[/yellow]")
            log_manager.close_all()
            raise typer.Exit(1)

    # Validate model parameter
    valid_models = ["opus", "sonnet", "haiku"]
    if model.lower() not in valid_models:
        log_and_print(log_manager, f"[red]Error: Invalid model: {model}[/red]", f"[red]Error: Invalid model: {model}[/red]")
        log_and_print(log_manager, f"[yellow]Valid models: {', '.join(valid_models)}[/yellow]", f"[yellow]Valid models: {', '.join(valid_models)}[/yellow]")
        log_manager.close_all()
        raise typer.Exit(1)

    # Validate max_turns if provided
    if max_turns is not None and max_turns < 1:
        log_and_print(log_manager, f"[red]Error: max_turns must be at least 1[/red]", f"[red]Error: max_turns must be at least 1[/red]")
        log_manager.close_all()
        raise typer.Exit(1)

    # Check if prompt is a file path or text
    prompt_text = prompt
    prompt_path = Path(prompt)
    try:
        # Try to check if it's a file first (avoids file name too long errors)
        if prompt_path.is_file():
            # Read file content
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
                log_and_print(log_manager, f"[green]Loaded prompt from file: {prompt_path}[/green]", f"[green]Loaded prompt from file: {prompt_path}[/green]")
            except Exception as e:
                log_and_print(log_manager, f"[red]Error reading prompt file: {e}[/red]", f"[red]Error reading prompt file: {e}[/red]")
                log_manager.close_all()
                raise typer.Exit(1)
        else:
            # Use as-is
            log_and_print(log_manager, "[green]Using provided prompt text[/green]", "[green]Using provided prompt text[/green]")
    except OSError:
        # Path is invalid (e.g., too long for filesystem), treat as text
        log_and_print(log_manager, "[green]Using provided prompt text[/green]", "[green]Using provided prompt text[/green]")

    # Display configuration table
    config_table = Table(title="Configuration", show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Repository", repo_url)
    config_table.add_row("Branch", branch)
    config_table.add_row("Forks", str(num_forks))
    config_table.add_row("Model", model)
    config_table.add_row("Max Turns", str(max_turns) if max_turns else "default")
    config_table.add_row("Prompt Preview", prompt_text[:100] + "..." if len(prompt_text) > 100 else prompt_text)

    console.print(config_table)
    log_manager.log_primary("")

    # === EXECUTION ===
    log_and_print(log_manager, "[bold yellow]Starting parallel fork execution...[/bold yellow]\n", "[bold yellow]Starting parallel fork execution...[/bold yellow]\n")

    try:
        # Call agents.run_forks_parallel()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Running {num_forks} fork(s) in parallel...", total=None)

            results = forks.run_forks_parallel(
                num_forks=num_forks,
                repo_url=repo_url,
                branch=branch,
                user_prompt=prompt_text,
                log_manager=log_manager,
                max_turns=max_turns,
                model=model,
            )

            progress.update(task, completed=True)

        log_and_print(log_manager, "[green]All forks completed![/green]\n", "[green]All forks completed![/green]\n")

    except Exception as e:
        log_and_print(log_manager, f"\n[red]Error during execution: {e}[/red]", f"\n[red]Error during execution: {e}[/red]")
        log_manager.close_all()
        raise typer.Exit(1)

    # === RESULTS ===
    # Collect all log file paths from LogManager
    log_paths = log_manager.get_all_log_paths()

    # Display results table
    results_table = Table(title="Execution Results", show_header=True, header_style="bold magenta")
    results_table.add_column("Fork", style="cyan", justify="center")
    results_table.add_column("Status", style="green")
    results_table.add_column("Cost", style="yellow", justify="right")
    results_table.add_column("Tokens (In/Out)", style="blue", justify="right")
    results_table.add_column("Log File", style="white")

    successful_forks = 0
    failed_forks = 0
    total_cost = 0.0

    for result in results:
        fork_num = result["fork_num"]
        status = result["status"]
        cost = result.get("cost", 0.0)
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)

        # Determine status style
        if status == "success":
            status_text = "[green]✓ Success[/green]"
            successful_forks += 1
        else:
            status_text = f"[red]✗ {status}[/red]"
            failed_forks += 1

        # Get log file path
        logger = log_manager.get_logger(fork_num)
        log_file = str(logger.log_path) if logger else "N/A"

        results_table.add_row(
            str(fork_num),
            status_text,
            f"${cost:.4f}",
            f"{input_tokens:,} / {output_tokens:,}",
            log_file,
        )

        total_cost += cost

    console.print(results_table)
    log_manager.log_primary("")

    # === VSCODE INTEGRATION ===
    if log_paths:
        log_and_print(log_manager, "[bold yellow]Opening log files in VSCode...[/bold yellow]", "[bold yellow]Opening log files in VSCode...[/bold yellow]")
        try:
            # Open all log files in VSCode
            log_paths_str = [str(p) for p in log_paths]
            subprocess.run(["code"] + log_paths_str, check=False)
            log_and_print(log_manager, "[green]Log files opened in VSCode[/green]\n", "[green]Log files opened in VSCode[/green]\n")
        except FileNotFoundError:
            log_and_print(log_manager, "[yellow]VSCode (code) not found in PATH. Please open log files manually.[/yellow]\n", "[yellow]VSCode (code) not found in PATH. Please open log files manually.[/yellow]\n")
        except Exception as e:
            log_and_print(log_manager, f"[yellow]Could not open VSCode: {e}[/yellow]\n", f"[yellow]Could not open VSCode: {e}[/yellow]\n")

    # === SUMMARY ===
    summary_panel = Panel(
        f"""[bold cyan]Summary[/bold cyan]

[green]Total Forks:[/green] {num_forks}
[green]Successful:[/green] {successful_forks}
[red]Failed:[/red] {failed_forks}
[yellow]Total Cost:[/yellow] ${total_cost:.4f}

[blue]Log Directory:[/blue] {constants.LOG_DIR}
        """,
        title="Execution Summary",
        border_style="cyan",
    )

    console.print(summary_panel)

    # Exit with appropriate code
    if failed_forks > 0:
        log_and_print(log_manager, f"\n[yellow]⚠️  {failed_forks} fork(s) failed. Check log files for details.[/yellow]", f"\n[yellow]⚠️  {failed_forks} fork(s) failed. Check log files for details.[/yellow]")
        # Close all loggers
        log_manager.close_all()
        sys.exit(1)
    else:
        log_and_print(log_manager, "\n[green]✓ All forks completed successfully![/green]", "\n[green]✓ All forks completed successfully![/green]")
        # Close all loggers
        log_manager.close_all()
        sys.exit(0)
