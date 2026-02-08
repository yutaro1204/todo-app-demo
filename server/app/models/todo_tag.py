"""
TodoTag association model for many-to-many relationship between TODOs and Tags.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base


class TodoTag(Base):
    """Association table linking TODOs to Tags."""

    __tablename__ = "todo_tags"

    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Unique constraint to prevent duplicate tag assignments
    __table_args__ = (UniqueConstraint("todo_id", "tag_id", name="uq_todo_tag"),)

    def __repr__(self) -> str:
        return f"<TodoTag(id={self.id}, todo_id={self.todo_id}, tag_id={self.tag_id})>"
