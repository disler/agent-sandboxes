"""
Custom exceptions for agent-sandboxes applications.

Provides a hierarchy of exceptions for better error handling
and debugging across all apps.
"""


class SandboxError(Exception):
    """Base exception for sandbox-related errors."""
    pass


class ConfigurationError(SandboxError):
    """Raised when configuration is invalid or missing."""
    pass


class ConnectionError(SandboxError):
    """Raised when sandbox connection fails."""
    pass


class SandboxTimeoutError(SandboxError):
    """Raised when sandbox operation times out."""
    pass


class SandboxNotFoundError(SandboxError):
    """Raised when sandbox ID is not found."""
    pass


class FileOperationError(SandboxError):
    """Raised when file operation fails in sandbox."""
    pass


class CommandExecutionError(SandboxError):
    """Raised when command execution fails in sandbox."""
    pass
