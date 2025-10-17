"""Label data model."""

from pydantic import BaseModel, Field


class Label(BaseModel):
    """Represents a label/tag for tickets."""

    id: str = Field(..., description="Unique label identifier")
    name: str = Field(..., description="Label name")
    description: str | None = Field(None, description="Label description")
    color: str | None = Field(None, description="Label color (hex code)")
