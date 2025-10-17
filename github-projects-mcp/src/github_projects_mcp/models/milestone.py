"""Milestone data model."""

from datetime import datetime

from pydantic import BaseModel, Field


class Milestone(BaseModel):
    """Represents a milestone for organizing tickets."""

    id: str = Field(..., description="Unique milestone identifier")
    title: str = Field(..., description="Milestone title")
    description: str | None = Field(None, description="Milestone description")
    state: str = Field(..., description="Milestone state (open/closed)")
    due_date: datetime | None = Field(None, description="Due date")
    url: str | None = Field(None, description="Milestone URL")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
