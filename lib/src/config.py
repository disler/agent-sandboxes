"""
Configuration management for agent-sandboxes applications.

Handles environment variable loading, configuration validation,
and provides consistent configuration access across apps.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


def find_project_root() -> Path:
    """
    Find the project root directory by looking for .env file.

    Returns:
        Path to project root directory
    """
    current = Path.cwd()

    # Walk up the directory tree looking for .env file
    for parent in [current] + list(current.parents):
        if (parent / ".env").exists():
            return parent
        if (parent / "pyproject.toml").exists() and (parent / "apps").exists():
            return parent

    # Fallback to current directory
    return current


def load_config(env_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Load configuration from .env file.

    Args:
        env_path: Optional path to .env file. If None, searches for project root.

    Returns:
        Dictionary of loaded environment variables
    """
    if env_path is None:
        root = find_project_root()
        env_path = root / ".env"

    if env_path.exists():
        load_dotenv(env_path, override=True)

    # Return relevant config vars
    return {
        "E2B_API_KEY": os.getenv("E2B_API_KEY", ""),
        "CLAUDE_CODE_OAUTH_TOKEN": os.getenv("CLAUDE_CODE_OAUTH_TOKEN", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
    }


def get_env_var(
    key: str,
    required: bool = False,
    default: Optional[str] = None
) -> Optional[str]:
    """
    Get environment variable with optional validation.

    Args:
        key: Environment variable name
        required: Whether the variable is required
        default: Default value if not found

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(key, default)

    if required and not value:
        raise ValueError(
            f"Required environment variable '{key}' is not set. "
            f"Please add it to your .env file."
        )

    return value


def get_e2b_api_key() -> str:
    """Get E2B API key from environment (required)."""
    return get_env_var("E2B_API_KEY", required=True)


def get_claude_auth() -> Dict[str, str]:
    """
    Get Claude authentication credentials.

    Returns dict with available auth methods:
    - CLAUDE_CODE_OAUTH_TOKEN (preferred)
    - ANTHROPIC_API_KEY (fallback)
    """
    auth = {}

    oauth_token = get_env_var("CLAUDE_CODE_OAUTH_TOKEN")
    if oauth_token:
        auth["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token

    api_key = get_env_var("ANTHROPIC_API_KEY")
    if api_key:
        auth["ANTHROPIC_API_KEY"] = api_key

    if not auth:
        raise ValueError(
            "No Claude authentication found. Set either CLAUDE_CODE_OAUTH_TOKEN "
            "or ANTHROPIC_API_KEY in your .env file."
        )

    return auth


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment (optional)."""
    return get_env_var("GITHUB_TOKEN", required=False)
