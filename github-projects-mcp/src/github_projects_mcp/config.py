"""Configuration management."""

import os
from typing import Any

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    github_token: str = Field(..., description="GitHub Personal Access Token")
    github_owner: str = Field(..., description="GitHub repository owner/organization")
    github_repo: str = Field(..., description="GitHub repository name")
    github_project_number: int | None = Field(
        None, description="Default GitHub Project number"
    )

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings from environment.

    Returns:
        Settings object with configuration values

    Raises:
        ValueError: If required environment variables are missing
    """
    return Settings()
