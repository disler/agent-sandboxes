"""
Shared library for agent-sandboxes applications.

Provides common functionality for E2B sandbox management, configuration,
logging, and utilities across all apps.
"""

from .config import load_config, get_env_var
from .sandbox import get_sandbox_connection, SandboxManager
from .errors import SandboxError, ConfigurationError, ConnectionError
from .logging import setup_logger, get_logger

__all__ = [
    "load_config",
    "get_env_var",
    "get_sandbox_connection",
    "SandboxManager",
    "SandboxError",
    "ConfigurationError",
    "ConnectionError",
    "setup_logger",
    "get_logger",
]

__version__ = "0.1.0"
