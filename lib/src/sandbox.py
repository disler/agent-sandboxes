"""
E2B sandbox connection and management utilities.

Provides helper functions for creating, connecting to, and managing
E2B sandbox instances with consistent error handling.
"""

from typing import Optional, Dict, Any
from e2b import Sandbox
from .config import get_e2b_api_key
from .errors import ConnectionError, SandboxNotFoundError


def get_sandbox_connection(
    sandbox_id: Optional[str] = None,
    template: str = "base",
    timeout: int = 300,
    envs: Optional[Dict[str, str]] = None,
    auto_pause: bool = False,
) -> Sandbox:
    """
    Create or connect to an E2B sandbox.

    Args:
        sandbox_id: Existing sandbox ID to connect to. If None, creates new sandbox.
        template: Template to use for new sandbox (ignored if sandbox_id provided)
        timeout: Sandbox timeout in seconds
        envs: Environment variables to set in sandbox
        auto_pause: Enable auto-pause (beta feature)

    Returns:
        Connected Sandbox instance

    Raises:
        ConnectionError: If connection fails
        SandboxNotFoundError: If sandbox_id not found
    """
    try:
        # Ensure API key is set
        get_e2b_api_key()

        if sandbox_id:
            # Connect to existing sandbox
            try:
                sandbox = Sandbox.connect(sandbox_id)
                return sandbox
            except Exception as e:
                raise SandboxNotFoundError(
                    f"Failed to connect to sandbox '{sandbox_id}': {e}"
                )
        else:
            # Create new sandbox
            create_kwargs = {
                "template": template,
                "timeout": timeout,
            }

            if envs:
                create_kwargs["envs"] = envs

            if auto_pause:
                create_kwargs["auto_pause"] = auto_pause

            sandbox = Sandbox.create(**create_kwargs)
            return sandbox

    except Exception as e:
        if isinstance(e, (ConnectionError, SandboxNotFoundError)):
            raise
        raise ConnectionError(f"Failed to create/connect sandbox: {e}")


class SandboxManager:
    """
    Context manager for E2B sandbox lifecycle.

    Ensures sandbox is properly cleaned up even if errors occur.

    Usage:
        with SandboxManager(template="base", timeout=600) as sbx:
            result = sbx.commands.run("python --version")
            print(result.stdout)
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        template: str = "base",
        timeout: int = 300,
        envs: Optional[Dict[str, str]] = None,
        auto_pause: bool = False,
        auto_kill: bool = True,
    ):
        """
        Initialize sandbox manager.

        Args:
            sandbox_id: Existing sandbox ID to connect to
            template: Template for new sandbox
            timeout: Sandbox timeout in seconds
            envs: Environment variables
            auto_pause: Enable auto-pause
            auto_kill: Automatically kill sandbox on exit
        """
        self.sandbox_id = sandbox_id
        self.template = template
        self.timeout = timeout
        self.envs = envs
        self.auto_pause = auto_pause
        self.auto_kill = auto_kill
        self.sandbox: Optional[Sandbox] = None

    def __enter__(self) -> Sandbox:
        """Create/connect to sandbox."""
        self.sandbox = get_sandbox_connection(
            sandbox_id=self.sandbox_id,
            template=self.template,
            timeout=self.timeout,
            envs=self.envs,
            auto_pause=self.auto_pause,
        )
        return self.sandbox

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up sandbox."""
        if self.sandbox and self.auto_kill:
            try:
                self.sandbox.kill()
            except:
                pass  # Best effort cleanup
        return False
