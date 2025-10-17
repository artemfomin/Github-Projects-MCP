"""Comment data model."""

from datetime import datetime

from pydantic import BaseModel, Field


class Comment(BaseModel):
    """Represents a comment on a ticket."""

    id: str = Field(..., description="Unique comment identifier")
    ticket_id: str = Field(..., description="Associated ticket ID")
    author: str = Field(..., description="Comment author username")
    body: str = Field(..., description="Comment text content")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    url: str | None = Field(None, description="Comment URL")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
