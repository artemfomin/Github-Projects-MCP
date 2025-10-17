"""Pytest configuration and fixtures."""

import os

import pytest
from dotenv import load_dotenv

from github_projects_mcp.github import GitHubProjectsClient

# Load environment variables
load_dotenv()


@pytest.fixture
def github_token() -> str:
    """Get GitHub token from environment.

    Returns:
        GitHub Personal Access Token

    Raises:
        ValueError: If GITHUB_TOKEN not set
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set in environment")
    return token


@pytest.fixture
def github_owner() -> str:
    """Get GitHub owner from environment.

    Returns:
        Repository owner name
    """
    return os.getenv("GITHUB_OWNER", "artemfomin")


@pytest.fixture
def github_repo() -> str:
    """Get GitHub repo from environment.

    Returns:
        Repository name
    """
    return os.getenv("GITHUB_REPO", "TestRepo")


@pytest.fixture
def github_client(github_token: str, github_owner: str, github_repo: str) -> GitHubProjectsClient:
    """Create GitHub Projects client instance.

    Args:
        github_token: GitHub Personal Access Token
        github_owner: Repository owner
        github_repo: Repository name

    Returns:
        Configured GitHubProjectsClient
    """
    return GitHubProjectsClient(
        token=github_token,
        owner=github_owner,
        repo=github_repo,
    )
