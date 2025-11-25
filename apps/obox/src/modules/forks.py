"""
Fork orchestration for parallel agent execution.

Handles threading and parallel execution of multiple sandbox forks.
"""

import asyncio
import threading
from .agents import SandboxForkAgent
from .logs import ForkLogger


def run_fork_in_thread(
    fork_num: int,
    repo_url: str,
    branch: str,
    user_prompt: str,
    logger: ForkLogger,
    max_turns: int | None = None,
    model: str | None = None,
) -> dict:
    """
    Run a single fork agent in a thread.

    Args:
        fork_num: Fork number
        repo_url: Git repository URL
        branch: Git branch
        user_prompt: User's prompt
        logger: Fork logger
        max_turns: Maximum conversation turns (None = use default)
        model: Claude model to use (None = use default)

    Returns:
        Execution result dictionary
    """
    # Create SandboxForkAgent
    agent = SandboxForkAgent(
        fork_num=fork_num,
        repo_url=repo_url,
        branch=branch,
        user_prompt=user_prompt,
        logger=logger,
        max_turns=max_turns,
        model=model,
    )

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()

    # Set event loop
    asyncio.set_event_loop(loop)

    try:
        # Run agent.execute() in event loop
        result = loop.run_until_complete(agent.execute())
    finally:
        # Close event loop
        loop.close()

    return result


def run_forks_parallel(
    num_forks: int,
    repo_url: str,
    branch: str,
    user_prompt: str,
    log_manager,
    max_turns: int | None = None,
    model: str | None = None,
) -> list[dict]:
    """
    Run multiple forks in parallel threads.

    Args:
        num_forks: Number of forks to run
        repo_url: Git repository URL
        branch: Git branch
        user_prompt: User's prompt
        log_manager: LogManager instance
        max_turns: Maximum conversation turns (None = use default)
        model: Claude model to use (None = use default)

    Returns:
        List of execution results (one per fork)
    """
    threads = []
    results = [None] * num_forks

    # Create and start threads
    for i in range(num_forks):
        fork_num = i + 1  # 1-indexed

        # Generate fork-specific branch name when multiple forks
        fork_branch = f"{branch}-{fork_num}" if num_forks > 1 else branch

        # Create logger from log_manager (with branch name)
        logger = log_manager.create_logger(fork_num, fork_branch)

        # Create wrapper function to store result
        def thread_target(fork_num=fork_num, logger=logger, fork_branch=fork_branch, result_index=i):
            result = run_fork_in_thread(
                fork_num=fork_num,
                repo_url=repo_url,
                branch=fork_branch,
                user_prompt=user_prompt,
                logger=logger,
                max_turns=max_turns,
                model=model,
            )
            results[result_index] = result

        # Create thread
        thread = threading.Thread(target=thread_target)

        # Start thread
        thread.start()

        # Add to threads list
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results
