"""
Repository for Todo data access.
"""

from sqlalchemy.orm import Session, joinedload
from app.models.todo import Todo, TodoStatus
from app.models.tag import Tag


class TodoRepository:
    """Repository for Todo database operations."""

    def __init__(self, db: Session) -> None:
        """
        Initialize TodoRepository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_id(self, todo_id: int) -> Todo | None:
        """
        Get TODO by ID with eager loading of tags.

        Args:
            todo_id: TODO ID to search for

        Returns:
            Todo instance if found, None otherwise
        """
        return (
            self.db.query(Todo)
            .options(joinedload(Todo.tags))
            .filter(Todo.id == todo_id)
            .first()
        )

    def get_all_for_user(
        self,
        user_id: int,
        status: str | None = None,
        tag_ids: list[int] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Todo]:
        """
        Get all TODOs for a user with optional filters.

        Args:
            user_id: User ID to filter by
            status: Optional status filter (pending, in_progress, completed)
            tag_ids: Optional list of tag IDs to filter by
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Todo instances matching the filters
        """
        query = self.db.query(Todo).filter(Todo.user_id == user_id)

        # Apply status filter
        if status:
            query = query.filter(Todo.status == status)

        # Apply tag filter
        if tag_ids:
            # Join with tags and filter by tag IDs
            # Use distinct() to avoid duplicate TODOs when multiple tags match
            query = query.join(Todo.tags).filter(Tag.id.in_(tag_ids)).distinct()

        # Eager load tags to avoid N+1 queries
        query = query.options(joinedload(Todo.tags))

        # Order by created_at DESC (newest first)
        query = query.order_by(Todo.created_at.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all()

    def create(
        self,
        user_id: int,
        title: str,
        description: str | None = None,
        status: TodoStatus = TodoStatus.PENDING,
        starts_date=None,
        expires_date=None,
        tag_ids: list[int] | None = None,
    ) -> Todo:
        """
        Create a new TODO.

        Args:
            user_id: ID of the user creating the TODO
            title: TODO title (required)
            description: Optional description
            status: TODO status (default: pending)
            starts_date: Optional start date
            expires_date: Optional expiration date
            tag_ids: Optional list of tag IDs to associate

        Returns:
            Created Todo instance
        """
        todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            starts_date=starts_date,
            expires_date=expires_date,
        )

        # Add tags if provided
        if tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            todo.tags = tags

        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo: Todo, **kwargs) -> Todo:
        """
        Update a TODO.

        Args:
            todo: Todo instance to update
            **kwargs: Fields to update

        Returns:
            Updated Todo instance
        """
        # Handle tag_ids separately
        tag_ids = kwargs.pop("tag_ids", None)
        if tag_ids is not None:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            todo.tags = tags

        # Update other fields
        for key, value in kwargs.items():
            if value is not None and hasattr(todo, key):
                setattr(todo, key, value)

        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        """
        Delete a TODO.

        Args:
            todo: Todo instance to delete
        """
        self.db.delete(todo)
        self.db.commit()
