"""
Pydantic schemas for TODO operations.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.todo import TodoStatus


class TagResponse(BaseModel):
    """Schema for Tag response."""

    id: int
    name: str
    color_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    """Schema for creating a new TODO."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: TodoStatus = TodoStatus.PENDING
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] = []

    @field_validator("expires_date")
    @classmethod
    def validate_dates(cls, v: datetime | None, info) -> datetime | None:
        """Validate that expires_date is after starts_date."""
        if v and info.data.get("starts_date") and v < info.data["starts_date"]:
            raise ValueError("expires_date must be after starts_date")
        return v


class TodoUpdate(BaseModel):
    """Schema for updating a TODO."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TodoStatus | None = None
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] | None = None

    @field_validator("expires_date")
    @classmethod
    def validate_dates(cls, v: datetime | None, info) -> datetime | None:
        """Validate that expires_date is after starts_date."""
        if v and info.data.get("starts_date") and v < info.data["starts_date"]:
            raise ValueError("expires_date must be after starts_date")
        return v


class TodoResponse(BaseModel):
    """Schema for TODO response."""

    id: int
    user_id: int
    title: str
    description: str | None
    status: TodoStatus
    starts_date: datetime | None
    expires_date: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True
