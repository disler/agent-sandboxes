"""
Git repository utilities for validation and operations.
"""

import re
from datetime import datetime
from typing import Tuple
from .constants import DEFAULT_BRANCH_TEMPLATE


def validate_git_url(url: str) -> bool:
    """
    Validate git repository URL format.

    Args:
        url: Git repository URL

    Returns:
        True if valid, False otherwise
    """
    # Check for common git URL patterns:
    # - https://github.com/user/repo
    # - https://github.com/user/repo.git
    # - git@github.com:user/repo.git
    # - https://gitlab.com/user/repo
    # - etc.

    # HTTPS pattern
    https_pattern = r'^https?://[\w\-\.]+(:\d+)?/[\w\-\.]+/[\w\-\.]+(\.git)?$'

    # SSH pattern
    ssh_pattern = r'^git@[\w\-\.]+:[\w\-\.]+/[\w\-\.]+(\.git)?$'

    # Check both patterns
    return bool(re.match(https_pattern, url) or re.match(ssh_pattern, url))


def parse_repo_name(url: str) -> str:
    """
    Extract repository name from URL.

    Args:
        url: Git repository URL

    Returns:
        Repository name (e.g., "myrepo")
    """
    # Remove .git suffix if present
    if url.endswith('.git'):
        url = url[:-4]

    # Extract last path component
    # Handle both HTTPS and SSH formats
    if '/' in url:
        # HTTPS format: https://github.com/user/repo
        repo_name = url.rstrip('/').split('/')[-1]
    elif ':' in url:
        # SSH format: git@github.com:user/repo
        repo_name = url.split(':')[-1].rstrip('/').split('/')[-1]
    else:
        # Fallback: use the whole URL
        repo_name = url

    return repo_name


def generate_branch_name() -> str:
    """
    Generate unique branch name with timestamp.

    Returns:
        Branch name string
    """
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    # Format using DEFAULT_BRANCH_TEMPLATE
    branch_name = DEFAULT_BRANCH_TEMPLATE.format(timestamp=timestamp)

    return branch_name


def validate_branch_name(branch: str) -> bool:
    """
    Validate branch name format.

    Args:
        branch: Branch name to validate

    Returns:
        True if valid, False otherwise
    """
    # Check for valid git branch name characters
    # No spaces, special characters except -_/
    # Cannot start with - or /
    # Cannot end with /
    # Cannot contain ..
    # Cannot contain @{
    # Cannot contain \

    if not branch:
        return False

    # Basic pattern for valid git branch names
    # Allow alphanumeric, dash, underscore, forward slash, dot
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9/_\.-]*[a-zA-Z0-9]$'

    # Check pattern match
    if not re.match(pattern, branch):
        return False

    # Check for invalid sequences
    invalid_sequences = ['..', '@{', '\\', '//']
    for seq in invalid_sequences:
        if seq in branch:
            return False

    return True
