"""
Todo model for task items.
"""

from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class TodoStatus(str, Enum):
    """Enum for TODO status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Todo(Base):
    """Todo task item model."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TodoStatus),
        nullable=False,
        default=TodoStatus.PENDING,
        index=True,
    )
    starts_date = Column(DateTime(timezone=True), nullable=True)
    expires_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="todos")
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")

    def __repr__(self) -> str:
        return f"<Todo(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"
