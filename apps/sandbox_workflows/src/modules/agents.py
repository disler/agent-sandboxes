"""
Claude Code agent creation and execution for sandbox forks.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
)
from .logs import ForkLogger
from .hooks import create_hook_dict
from .constants import (
    SYSTEM_PROMPT_PATH,
    MCP_CONFIG_PATH,
    DEFAULT_MAX_TURNS,
    ALLOWED_TOOLS,
    DISALLOWED_TOOLS,
    WORKING_DIR,
    ALLOWED_DIRECTORIES,
)


class SandboxForkAgent:
    """
    Claude Code agent that executes user prompt in an isolated sandbox.

    Features:
    - Hybrid tool access (MCP + local with restrictions)
    - Full observability through hooks
    - Path gating for local file operations
    """

    def __init__(
        self,
        fork_num: int,
        repo_url: str,
        branch: str,
        user_prompt: str,
        logger: ForkLogger,
        max_turns: int | None = None,
        model: str | None = None,
    ):
        """
        Initialize sandbox fork agent.

        Args:
            fork_num: Fork number (1-indexed)
            repo_url: Git repository URL to clone
            branch: Git branch to checkout
            user_prompt: User's prompt to execute
            logger: Logger instance for this fork
            max_turns: Maximum conversation turns (None = use default)
            model: Claude model to use (None = use default)
        """
        self.fork_num = fork_num
        self.repo_url = repo_url
        self.branch = branch
        self.user_prompt = user_prompt
        self.logger = logger
        self.max_turns = max_turns if max_turns is not None else DEFAULT_MAX_TURNS
        self.model = model

        # Load system prompt and format with repo/branch
        self.system_prompt = self._load_system_prompt()

        # Build hooks for observability and path gating
        hooks_dict = create_hook_dict(logger)

        # Prepare environment variables for sandbox
        agent_env = {}
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            agent_env["GITHUB_TOKEN"] = github_token

        # Build ClaudeAgentOptions
        self.options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            mcp_servers=str(MCP_CONFIG_PATH),  # Path to .mcp.json
            allowed_tools=ALLOWED_TOOLS,
            disallowed_tools=DISALLOWED_TOOLS,
            hooks=hooks_dict,  # Install all hooks
            permission_mode="acceptEdits",
            max_turns=self.max_turns,
            model=self.model,
            env=agent_env,  # Pass GITHUB_TOKEN to agent
            cwd=str(WORKING_DIR),
            setting_sources=["project"],  # Enable project-level slash commands
        )

    def _load_system_prompt(self) -> str:
        """
        Load system prompt from markdown file and format with repo/branch/github_token/allowed_directories.

        Returns:
            Formatted system prompt text
        """
        try:
            with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                template = f.read()

            # Format allowed directories as a bulleted list
            allowed_dirs_list = "\n".join(
                [f"- `{d.name}/`" for d in ALLOWED_DIRECTORIES]
            )

            # Get GitHub token from environment
            github_token = os.getenv("GITHUB_TOKEN", "")

            # Format with repo_url, branch, fork_number, github_token, and allowed_directories
            return template.format(
                repo_url=self.repo_url,
                branch=self.branch,
                fork_number=self.fork_num,
                github_token=github_token,
                allowed_directories=allowed_dirs_list,
            )
        except Exception as e:
            self.logger.log_error(e)
            return "You are a helpful AI assistant."

    async def execute(self) -> dict:
        """
        Execute the agent in the sandbox.

        Returns:
            Execution result with status, cost, tokens, etc.
        """
        self.logger.log("INFO", "=== Starting agent execution ===")
        self.logger.log("INFO", f"Repository: {self.repo_url}")
        self.logger.log("INFO", f"Branch: {self.branch}")
        self.logger.log(
            "INFO", f"Model: {self.model if self.model else 'default (sonnet)'}"
        )
        self.logger.log("INFO", f"Max Turns: {self.max_turns}")

        # Log user prompt
        self.logger.log("INFO", "=== User Prompt ===")
        self.logger.log("INFO", self.user_prompt)

        # Log system prompt
        self.logger.log("INFO", "=== System Prompt ===")
        self.logger.log("INFO", self.system_prompt)

        result = {
            "fork_num": self.fork_num,
            "status": "unknown",
            "error": None,
            "cost": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
        }

        client = None
        try:
            # Create ClaudeSDKClient with options
            client = ClaudeSDKClient(self.options)

            # Connect to client
            await client.connect()
            self.logger.log("INFO", "Connected to Claude SDK client")

            # Submit user prompt directly
            await client.query(self.user_prompt)
            self.logger.log("INFO", "Query submitted to agent")

            # Stream messages and log each
            async for message in client.receive_response():
                self._log_message(message)

                # Check for ResultMessage to extract cost/tokens
                if isinstance(message, ResultMessage):
                    # Extract cost from top-level field first (preferred)
                    total_cost = getattr(message, "total_cost_usd", None) or 0.0

                    # Extract token counts from usage dict/object
                    if message.usage:
                        usage = message.usage
                        if isinstance(usage, dict):
                            result["input_tokens"] = usage.get("input_tokens", 0)
                            result["output_tokens"] = usage.get("output_tokens", 0)
                            # Fall back to usage cost if top-level is None/0.0
                            if total_cost == 0.0:
                                total_cost = usage.get("total_cost_usd", 0.0)
                        else:
                            result["input_tokens"] = getattr(usage, "input_tokens", 0)
                            result["output_tokens"] = getattr(usage, "output_tokens", 0)
                            # Fall back to usage cost if top-level is None/0.0
                            if total_cost == 0.0:
                                total_cost = getattr(usage, "total_cost_usd", 0.0)

                    result["cost"] = total_cost

                    # Check error status from ResultMessage
                    is_error = getattr(message, "is_error", False)
                    result["status"] = "error" if is_error else "success"

                    self.logger.log(
                        "INFO",
                        "Agent execution completed",
                        is_error=is_error,
                        status=result["status"],
                        input_tokens=result["input_tokens"],
                        output_tokens=result["output_tokens"],
                        cost=f"${result['cost']:.4f}",
                    )

            # Disconnect client
            await client.disconnect()
            self.logger.log("INFO", "Disconnected from Claude SDK client")

        except Exception as e:
            self.logger.log_error(e)
            result["status"] = "error"
            result["error"] = str(e)

        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass

        return result

    def _log_message(self, message):
        """
        Log agent message to fork logger.

        Args:
            message: Message from agent
        """
        # Handle different message types
        if isinstance(message, UserMessage):
            # Log user messages
            if isinstance(message.content, str):
                self.logger.log_agent_message("User", message.content)
            else:
                # Content is a list of blocks - handle all ContentBlock types
                for block in message.content:
                    if isinstance(block, TextBlock):
                        self.logger.log_agent_message("User.TextBlock", block.text)
                    elif isinstance(block, ThinkingBlock):
                        self.logger.log_agent_message(
                            "User.ThinkingBlock", block.thinking
                        )
                    elif isinstance(block, ToolUseBlock):
                        self.logger.log_agent_message(
                            "User.ToolUseBlock", f"{block.name}({str(block.input)})"
                        )
                    elif isinstance(block, ToolResultBlock):
                        result_str = f"tool_use_id={block.tool_use_id}"
                        if block.is_error:
                            result_str += f" | ERROR: {block.content}"
                        else:
                            content_str = (
                                str(block.content) if block.content else "No output"
                            )
                            result_str += f" | {content_str}"
                        self.logger.log_agent_message(
                            "User.ToolResultBlock", result_str
                        )

        elif isinstance(message, AssistantMessage):
            # Log all content blocks
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.logger.log_agent_message("TextBlock", block.text)
                elif isinstance(block, ThinkingBlock):
                    self.logger.log_agent_message("ThinkingBlock", block.thinking)
                elif isinstance(block, ToolUseBlock):
                    self.logger.log_agent_message(
                        "ToolUseBlock", f"{block.name}({str(block.input)})"
                    )
                elif isinstance(block, ToolResultBlock):
                    # Log tool results with error status
                    result_str = f"tool_use_id={block.tool_use_id}"
                    if block.is_error:
                        result_str += f" | ERROR: {block.content}"
                    else:
                        content_str = (
                            str(block.content) if block.content else "No output"
                        )
                        result_str += f" | {content_str}"
                    self.logger.log_agent_message("ToolResultBlock", result_str)

        elif isinstance(message, SystemMessage):
            self.logger.log("INFO", "[System] Message received")

        elif isinstance(message, ResultMessage):
            self.logger.log(
                "INFO",
                "[Result] Agent completed turn",
                is_error=message.is_error,
                num_turns=message.num_turns,
            )
