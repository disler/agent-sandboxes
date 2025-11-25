"""
Thread-safe logging utilities for fork execution.
"""

import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional
from .constants import LOG_DIR, LOG_FILE_TEMPLATE, LOG_TIMESTAMP_FORMAT


class ForkLogger:
    """
    Thread-safe logger for individual fork execution.

    Manages log file creation, writing, and formatting for a single fork.
    """

    def __init__(self, fork_num: int, repo_name: str, branch: str):
        """
        Initialize fork logger.

        Args:
            fork_num: Fork number (1-indexed)
            repo_name: Repository name for context
            branch: Git branch name
        """
        self.fork_num = fork_num
        self.repo_name = repo_name
        self.branch = branch

        # Generate timestamp for log file name
        timestamp = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)

        # Create log file path using template
        log_filename = LOG_FILE_TEMPLATE.format(branch=branch, fork_num=fork_num, timestamp=timestamp)
        self._log_path = LOG_DIR / log_filename

        # Initialize thread lock for safe writing
        self._lock = threading.Lock()

        # Create log directory if it doesn't exist
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Open log file in write mode
        self._file = open(self._log_path, 'w', encoding='utf-8')

        # Write header with fork info
        self._write_header()

    def _write_header(self):
        """Write log file header."""
        header = f"""
{'=' * 80}
FORK #{self.fork_num} - {self.repo_name}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

"""
        self._file.write(header)
        self._file.flush()

    def log(self, level: str, message: str, **kwargs):
        """
        Write a log entry with timestamp and level.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            **kwargs: Additional key-value pairs to log
        """
        with self._lock:
            # Format timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # Format message with level and timestamp
            log_entry = f"[{timestamp}] [{level:7s}] {message}"

            # Add kwargs if present
            if kwargs:
                kwargs_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
                log_entry += f" | {kwargs_str}"

            log_entry += "\n"

            # Write to log file
            self._file.write(log_entry)

            # Flush buffer for real-time monitoring
            self._file.flush()

    def log_agent_message(self, message_type: str, content: str):
        """
        Log agent message in structured format.

        Args:
            message_type: Type of message (TextBlock, ToolUseBlock, etc.)
            content: Message content
        """
        # Log full content without truncation
        self.log(
            "INFO",
            f"[Agent] {message_type}",
            content=content
        )

    def log_error(self, error: Exception):
        """
        Log error with full traceback.

        Args:
            error: Exception to log
        """
        # Format exception with traceback
        error_msg = f"{type(error).__name__}: {str(error)}"
        tb = traceback.format_exc()

        self.log(
            "ERROR",
            error_msg,
            traceback=tb
        )

    def close(self):
        """Close log file and release resources."""
        with self._lock:
            # Write footer
            footer = f"""
{'=' * 80}
FORK #{self.fork_num} - COMPLETED
Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""
            self._file.write(footer)

            # Close file handle
            self._file.close()

    @property
    def log_path(self) -> Path:
        """Get path to log file."""
        return self._log_path


class PrimaryLogger:
    """
    Logger for primary/system-level execution (captures console output).
    Separate from fork-specific agent logs.
    """

    def __init__(self, repo_name: str):
        """
        Initialize primary logger.

        Args:
            repo_name: Repository name for context
        """
        self.repo_name = repo_name

        # Generate timestamp for log file name
        timestamp = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)

        # Create primary log file path
        log_filename = f"primary-{repo_name}-{timestamp}.log"
        self._log_path = LOG_DIR / log_filename

        # Initialize thread lock for safe writing
        self._lock = threading.Lock()

        # Create log directory if it doesn't exist
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Open log file in write mode
        self._file = open(self._log_path, 'w', encoding='utf-8')

        # Write header
        self._write_header()

    def _write_header(self):
        """Write log file header."""
        header = f"""
{'=' * 80}
PRIMARY EXECUTION LOG - {self.repo_name}
System-level messages (validation, configuration, results)
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

"""
        self._file.write(header)
        self._file.flush()

    def log(self, message: str):
        """
        Write a log entry with timestamp.

        Args:
            message: Log message (can be multiline)
        """
        with self._lock:
            # Format timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # Write each line with timestamp
            for line in message.splitlines():
                log_entry = f"[{timestamp}] {line}\n"
                self._file.write(log_entry)

            # Flush buffer for real-time monitoring
            self._file.flush()

    def close(self):
        """Close log file and release resources."""
        with self._lock:
            # Write footer
            footer = f"""
{'=' * 80}
PRIMARY EXECUTION LOG - COMPLETED
Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""
            self._file.write(footer)

            # Close file handle
            self._file.close()

    @property
    def log_path(self) -> Path:
        """Get path to log file."""
        return self._log_path


class LogManager:
    """
    Manager for creating and tracking multiple fork loggers.
    """

    def __init__(self, repo_name: str):
        """
        Initialize log manager.

        Args:
            repo_name: Repository name for context
        """
        self.repo_name = repo_name

        # Initialize dict to track loggers by fork number
        self._loggers: dict[int, ForkLogger] = {}

        # Create primary logger for system-level messages
        self._primary_logger = PrimaryLogger(repo_name)

        # Ensure log directory exists
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def create_logger(self, fork_num: int, branch: str) -> ForkLogger:
        """
        Create logger for a fork.

        Args:
            fork_num: Fork number
            branch: Git branch name

        Returns:
            ForkLogger instance
        """
        # Create ForkLogger instance
        logger = ForkLogger(fork_num, self.repo_name, branch)

        # Store in tracking dict
        self._loggers[fork_num] = logger

        # Return logger
        return logger

    def get_logger(self, fork_num: int) -> Optional[ForkLogger]:
        """Get logger for fork number."""
        return self._loggers.get(fork_num)

    def log_primary(self, message: str):
        """
        Log to primary execution log (system-level messages).

        Args:
            message: Message to log
        """
        self._primary_logger.log(message)

    def get_all_log_paths(self) -> list[Path]:
        """Get paths to all log files (primary + forks)."""
        paths = [self._primary_logger.log_path]
        paths.extend([logger.log_path for logger in self._loggers.values()])
        return paths

    def close_all(self):
        """Close all loggers (primary + forks)."""
        self._primary_logger.close()
        for logger in self._loggers.values():
            logger.close()
