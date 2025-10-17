"""Ticket data model."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    """Ticket status enumeration."""

    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    BACKLOG = "Backlog"


class Ticket(BaseModel):
    """Represents a task/issue ticket."""

    id: str = Field(..., description="Unique ticket identifier")
    number: int | None = Field(None, description="Ticket number")
    title: str = Field(..., description="Ticket title")
    body: str | None = Field(None, description="Ticket description/body")
    status: TicketStatus | str = Field(..., description="Current ticket status")
    labels: list[str] = Field(default_factory=list, description="Associated labels/tags")
    assignees: list[str] = Field(default_factory=list, description="Assigned users")
    milestone: str | None = Field(None, description="Associated milestone")
    branch: str | None = Field(None, description="Associated branch name")
    pull_requests: list[str] = Field(
        default_factory=list, description="Associated pull request URLs"
    )
    subtasks: list[str] = Field(default_factory=list, description="Subtask IDs")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    url: str | None = Field(None, description="Ticket URL")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
