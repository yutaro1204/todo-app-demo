"""
Todo service for business logic.
"""

from app.repositories.todo_repository import TodoRepository
from app.models.todo import Todo, TodoStatus
from app.schemas.todo import TodoCreate, TodoUpdate
from app.core.exceptions import TodoNotFoundError, UnauthorizedAccessError


class TodoService:
    """Service for TODO business logic."""

    def __init__(self, todo_repo: TodoRepository) -> None:
        """
        Initialize TodoService.

        Args:
            todo_repo: TodoRepository instance
        """
        self.todo_repo = todo_repo

    def get_todos_for_user(
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
            user_id: User ID to get TODOs for
            status: Optional status filter (pending, in_progress, completed)
            tag_ids: Optional list of tag IDs to filter by
            limit: Maximum number of results (default: 50, max: 100)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Todo instances matching the filters

        Raises:
            ValueError: If status is invalid or limit exceeds maximum
        """
        # Validate status if provided
        if status:
            try:
                TodoStatus(status)
            except ValueError:
                raise ValueError(
                    f"Invalid status: {status}. Must be one of: pending, in_progress, completed"
                )

        # Cap limit at 100
        if limit > 100:
            limit = 100

        # Delegate to repository
        return self.todo_repo.get_all_for_user(
            user_id=user_id,
            status=status,
            tag_ids=tag_ids,
            limit=limit,
            offset=offset,
        )

    def get_todo(self, todo_id: int, user_id: int) -> Todo:
        """
        Get a TODO by ID with authorization check.

        Args:
            todo_id: TODO ID to retrieve
            user_id: User ID making the request

        Returns:
            Todo instance

        Raises:
            TodoNotFoundError: If TODO doesn't exist
            UnauthorizedAccessError: If TODO belongs to different user
        """
        todo = self.todo_repo.get_by_id(todo_id)

        if not todo:
            raise TodoNotFoundError(f"TODO with id {todo_id} not found")

        if todo.user_id != user_id:
            raise UnauthorizedAccessError("You don't have permission to access this TODO")

        return todo

    def create_todo(self, user_id: int, data: TodoCreate) -> Todo:
        """
        Create a new TODO.

        Args:
            user_id: User ID creating the TODO
            data: TODO creation data

        Returns:
            Created Todo instance

        Raises:
            ValueError: If validation fails (e.g., expires_date before starts_date)
        """
        # Pydantic validation already ensures expires_date > starts_date
        return self.todo_repo.create(
            user_id=user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            starts_date=data.starts_date,
            expires_date=data.expires_date,
            tag_ids=data.tag_ids if data.tag_ids else None,
        )

    def update_todo(self, todo_id: int, user_id: int, data: TodoUpdate) -> Todo:
        """
        Update a TODO with authorization check.

        Args:
            todo_id: TODO ID to update
            user_id: User ID making the request
            data: Update data

        Returns:
            Updated Todo instance

        Raises:
            TodoNotFoundError: If TODO doesn't exist
            UnauthorizedAccessError: If TODO belongs to different user
            ValueError: If validation fails
        """
        # Get and verify authorization
        todo = self.get_todo(todo_id, user_id)

        # Prepare update data (only non-None fields)
        update_data = data.model_dump(exclude_unset=True)

        # Update the TODO
        return self.todo_repo.update(todo, **update_data)

    def delete_todo(self, todo_id: int, user_id: int) -> None:
        """
        Delete a TODO with authorization check.

        Args:
            todo_id: TODO ID to delete
            user_id: User ID making the request

        Raises:
            TodoNotFoundError: If TODO doesn't exist
            UnauthorizedAccessError: If TODO belongs to different user
        """
        # Get and verify authorization
        todo = self.get_todo(todo_id, user_id)

        # Delete the TODO
        self.todo_repo.delete(todo)
