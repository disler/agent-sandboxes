"""
Utility functions for agent-sandboxes applications.

Provides common helper functions used across multiple apps.
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_repo_url(url: str) -> bool:
    """
    Validate if a string is a valid git repository URL.

    Args:
        url: URL to validate

    Returns:
        True if valid git URL, False otherwise
    """
    # Check for common git URL patterns
    git_patterns = [
        r"^https?://github\.com/[\w\-]+/[\w\-\.]+",
        r"^git@github\.com:[\w\-]+/[\w\-\.]+\.git$",
        r"^https?://gitlab\.com/[\w\-]+/[\w\-\.]+",
        r"^https?://bitbucket\.org/[\w\-]+/[\w\-\.]+",
    ]

    return any(re.match(pattern, url) for pattern in git_patterns)


def validate_branch_name(branch: str) -> bool:
    """
    Validate if a string is a valid git branch name.

    Args:
        branch: Branch name to validate

    Returns:
        True if valid branch name, False otherwise
    """
    # Basic git branch name rules
    if not branch:
        return False

    # Cannot start with -, ., or /
    if branch[0] in "-./":
        return False

    # Cannot end with .lock or /
    if branch.endswith(".lock") or branch.endswith("/"):
        return False

    # Cannot contain certain characters
    invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
    if any(char in branch for char in invalid_chars):
        return False

    return True


def sanitize_branch_name(branch: str) -> str:
    """
    Sanitize a string to be a valid git branch name.

    Args:
        branch: Branch name to sanitize

    Returns:
        Sanitized branch name
    """
    # Replace invalid characters with -
    sanitized = re.sub(r"[~^:?*\[\\\s]+", "-", branch)

    # Remove leading/trailing special characters
    sanitized = sanitized.strip("-./")

    # Remove ..
    sanitized = sanitized.replace("..", "-")

    # Remove .lock suffix
    if sanitized.endswith(".lock"):
        sanitized = sanitized[:-5]

    return sanitized


def format_sandbox_id(sandbox_id: str) -> str:
    """
    Format sandbox ID for display (truncate if too long).

    Args:
        sandbox_id: Full sandbox ID

    Returns:
        Formatted sandbox ID
    """
    if len(sandbox_id) <= 12:
        return sandbox_id
    return f"{sandbox_id[:8]}...{sandbox_id[-4:]}"


def parse_model_name(model: Optional[str]) -> str:
    """
    Parse and validate model name, returning full model ID.

    Args:
        model: Short model name (opus, sonnet, haiku) or full model ID

    Returns:
        Full model ID

    Raises:
        ValueError: If model name is invalid
    """
    if not model:
        return "claude-sonnet-4-5-20250929"

    model_map = {
        "opus": "claude-opus-4-20250514",
        "sonnet": "claude-sonnet-4-5-20250929",
        "haiku": "claude-3-5-haiku-20241022",
    }

    # Return mapped name or assume it's already a full model ID
    return model_map.get(model.lower(), model)


def format_cost(cost_usd: float) -> str:
    """
    Format cost in USD for display.

    Args:
        cost_usd: Cost in USD

    Returns:
        Formatted cost string
    """
    return f"${cost_usd:.4f}"


def format_token_count(tokens: int) -> str:
    """
    Format token count for display.

    Args:
        tokens: Number of tokens

    Returns:
        Formatted token string
    """
    if tokens < 1000:
        return str(tokens)
    elif tokens < 1_000_000:
        return f"{tokens / 1000:.1f}K"
    else:
        return f"{tokens / 1_000_000:.1f}M"
