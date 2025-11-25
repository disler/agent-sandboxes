"""
Hook implementations for tool observability and path restrictions.

Hooks provide:
1. Full observability - Log ALL tool usage to fork logs
2. Path gating - Restrict Read/Write/Edit to allowed directories only
   (temp/, specs/, ai_docs/, app_docs/)
3. Security - Prevent accidental local filesystem access outside allowed directories
"""

from pathlib import Path
from typing import Any, Dict, Optional
from .constants import PATH_RESTRICTED_TOOLS, TEMP_DIR, TEMP_DIR_NAME, ALLOWED_DIRECTORIES
from .logs import ForkLogger


def create_pre_tool_hook(logger: ForkLogger):
    """
    Create PreToolUse hook for logging and path validation.

    This hook runs BEFORE any tool is executed.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def pre_tool_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PreToolUse hook implementation.

        Logs tool usage and validates file paths for restricted tools.

        Args:
            input_data: Dict with 'tool_name' and 'tool_input'
            tool_use_id: Tool use ID from Claude
            context: Hook context

        Returns:
            Hook response dict (may contain 'decision': 'block' to deny)
        """
        # Extract tool name and input
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Log the tool usage
        logger.log(
            "INFO",
            f"[PreToolUse] {tool_name}",
            tool_use_id=tool_use_id,
            tool_input=str(tool_input)
        )

        # === PATH VALIDATION FOR RESTRICTED TOOLS ===
        if tool_name in PATH_RESTRICTED_TOOLS:
            # Extract file_path from tool input
            file_path_str = tool_input.get("file_path")

            if not file_path_str:
                # No file_path provided - shouldn't happen but allow
                logger.log("WARNING", f"{tool_name} called without file_path")
                return {}

            # Convert to Path and resolve to absolute path
            file_path = Path(file_path_str).resolve()

            # Check if path is within any ALLOWED_DIRECTORIES
            is_allowed = False
            allowed_dir_name = None

            for allowed_dir in ALLOWED_DIRECTORIES:
                try:
                    # Check if file_path is relative to this allowed directory
                    file_path.relative_to(allowed_dir.resolve())
                    # Path is within this allowed directory
                    is_allowed = True
                    allowed_dir_name = allowed_dir.name
                    break
                except ValueError:
                    # Not in this directory, try next
                    continue

            if is_allowed:
                # Path is within an allowed directory - allow
                logger.log(
                    "DEBUG",
                    f"[PathValidation] {tool_name} path OK ({allowed_dir_name}/): {file_path_str}"
                )
                return {}  # Allow
            else:
                # Path is OUTSIDE all allowed directories - BLOCK
                allowed_names = ", ".join([d.name for d in ALLOWED_DIRECTORIES])
                logger.log(
                    "ERROR",
                    f"[PathValidation] BLOCKED {tool_name} - path outside allowed directories: {file_path_str}",
                    reason=f"Path must be within {allowed_names}"
                )

                # Return block decision
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"Path '{file_path_str}' is outside the allowed directories ({allowed_names}). "
                            f"All local file operations must be within these directories. "
                            f"Use MCP sandbox tools (mcp__e2b-sandbox__*) for sandbox operations."
                        )
                    }
                }

        # === BASH COMMAND LOGGING ===
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            logger.log(
                "INFO",
                f"[Bash] Executing local command",
                command=command
            )

        # === MCP TOOL LOGGING ===
        elif tool_name.startswith("mcp__e2b-sandbox__"):
            # Log MCP sandbox operations
            logger.log(
                "INFO",
                f"[SandboxOp] {tool_name}",
                sandbox_operation=tool_name.replace("mcp__e2b-sandbox__", "")
            )

        # Allow tool execution
        return {}

    return pre_tool_hook


def create_post_tool_hook(logger: ForkLogger):
    """
    Create PostToolUse hook for logging tool results.

    This hook runs AFTER any tool is executed.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def post_tool_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PostToolUse hook implementation.

        Logs tool results and any errors.

        Args:
            input_data: Dict with 'tool_name', 'result', 'is_error'
            tool_use_id: Tool use ID
            context: Hook context

        Returns:
            Empty dict (PostToolUse cannot block)
        """
        # Extract tool info
        tool_name = input_data.get("tool_name", "unknown")
        result = input_data.get("result")
        is_error = input_data.get("is_error", False)

        # Log based on success/failure
        if is_error:
            logger.log(
                "ERROR",
                f"[PostToolUse] {tool_name} FAILED",
                tool_use_id=tool_use_id,
                error=str(result)
            )
        else:
            logger.log(
                "INFO",
                f"[PostToolUse] {tool_name} completed",
                tool_use_id=tool_use_id,
                result=str(result) if result else "No result"
            )

        # === FILE TRACKING (Optional Enhancement) ===
        # Track which files were modified/read
        if tool_name in {"Write", "Edit"}:
            file_path = input_data.get("tool_input", {}).get("file_path")
            if file_path:
                logger.log(
                    "DEBUG",
                    f"[FileTracking] Modified: {file_path}"
                )
        elif tool_name == "Read":
            file_path = input_data.get("tool_input", {}).get("file_path")
            if file_path:
                logger.log(
                    "DEBUG",
                    f"[FileTracking] Read: {file_path}"
                )

        return {}

    return post_tool_hook


def create_user_prompt_hook(logger: ForkLogger):
    """
    Create UserPromptSubmit hook for logging user prompts.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def user_prompt_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        UserPromptSubmit hook - logs when user submits a prompt.

        Args:
            input_data: Dict with 'prompt'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict (cannot modify prompt)
        """
        prompt = input_data.get("prompt", "")
        logger.log(
            "INFO",
            "[UserPromptSubmit] Agent received prompt",
            prompt_length=len(prompt),
            prompt=prompt
        )
        return {}

    return user_prompt_hook


def create_stop_hook(logger: ForkLogger):
    """
    Create Stop hook for logging agent session end.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def stop_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        Stop hook - logs when agent session ends.

        Args:
            input_data: Dict with 'reason', 'num_turns', 'duration_ms'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        reason = input_data.get("reason", "unknown")
        num_turns = input_data.get("num_turns", 0)
        duration_ms = input_data.get("duration_ms", 0)

        logger.log(
            "INFO",
            "[Stop] Agent session ended",
            reason=reason,
            num_turns=num_turns,
            duration_seconds=duration_ms / 1000
        )
        return {}

    return stop_hook


def create_subagent_stop_hook(logger: ForkLogger):
    """
    Create SubagentStop hook for logging subagent completions.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def subagent_stop_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        SubagentStop hook - logs when subagent (Task tool) completes.

        Args:
            input_data: Dict with 'subagent_id'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        subagent_id = input_data.get("subagent_id", "unknown")
        logger.log(
            "INFO",
            "[SubagentStop] Subagent completed",
            subagent_id=subagent_id
        )
        return {}

    return subagent_stop_hook


def create_pre_compact_hook(logger: ForkLogger):
    """
    Create PreCompact hook for logging context compaction.

    Args:
        logger: Fork logger instance

    Returns:
        Hook callback function
    """

    async def pre_compact_hook(
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Any
    ) -> Dict[str, Any]:
        """
        PreCompact hook - logs before context window compaction.

        Args:
            input_data: Dict with 'tokens_before'
            tool_use_id: None for this hook
            context: Hook context

        Returns:
            Empty dict
        """
        tokens_before = input_data.get("tokens_before", 0)
        logger.log(
            "WARNING",
            "[PreCompact] Context compaction triggered",
            tokens_before=tokens_before,
            message="Agent is compacting conversation history to fit context window"
        )
        return {}

    return pre_compact_hook


def create_hook_dict(logger: ForkLogger) -> Dict[str, Any]:
    """
    Create complete hooks dictionary for ClaudeAgentOptions.

    Registers ALL available hook types for maximum observability:
    - PreToolUse: Log and validate before tool execution
    - PostToolUse: Log tool results
    - UserPromptSubmit: Log when prompts are submitted
    - Stop: Log when agent session ends
    - SubagentStop: Log when subagents complete
    - PreCompact: Log context compaction events

    Args:
        logger: Fork logger instance

    Returns:
        Hooks dict with all hooks configured
    """
    from claude_agent_sdk import HookMatcher

    return {
        "PreToolUse": [
            HookMatcher(hooks=[create_pre_tool_hook(logger)])
        ],
        "PostToolUse": [
            HookMatcher(hooks=[create_post_tool_hook(logger)])
        ],
        "UserPromptSubmit": [
            HookMatcher(hooks=[create_user_prompt_hook(logger)])
        ],
        "Stop": [
            HookMatcher(hooks=[create_stop_hook(logger)])
        ],
        "SubagentStop": [
            HookMatcher(hooks=[create_subagent_stop_hook(logger)])
        ],
        "PreCompact": [
            HookMatcher(hooks=[create_pre_compact_hook(logger)])
        ],
    }
