"""
Unit tests for TodoService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.todo_service import TodoService
from app.models.todo import Todo, TodoStatus
from app.schemas.todo import TodoCreate, TodoUpdate
from app.core.exceptions import TodoNotFoundError, UnauthorizedAccessError


@pytest.fixture
def mock_todo_repo():
    """Create a mock TodoRepository."""
    return Mock()


@pytest.fixture
def todo_service(mock_todo_repo):
    """Create TodoService with mocked repository."""
    return TodoService(mock_todo_repo)


def create_mock_todo(
    todo_id=1,
    user_id=1,
    title="Test TODO",
    status=TodoStatus.PENDING,
    tags=None,
):
    """Helper to create a mock TODO."""
    todo = Mock(spec=Todo)
    todo.id = todo_id
    todo.user_id = user_id
    todo.title = title
    todo.status = status
    todo.tags = tags or []
    return todo


class TestGetTodosForUser:
    """Tests for get_todos_for_user method."""

    def test_get_todos_no_filters(self, todo_service, mock_todo_repo):
        """Test getting all TODOs without filters."""
        # Arrange
        mock_todos = [
            create_mock_todo(1, 1, "TODO 1"),
            create_mock_todo(2, 1, "TODO 2"),
        ]
        mock_todo_repo.get_all_for_user.return_value = mock_todos

        # Act
        result = todo_service.get_todos_for_user(user_id=1)

        # Assert
        assert len(result) == 2
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status=None,
            tag_ids=None,
            limit=50,
            offset=0,
        )

    def test_get_todos_with_status_filter(self, todo_service, mock_todo_repo):
        """Test filtering TODOs by status."""
        # Arrange
        mock_todos = [create_mock_todo(1, 1, "TODO 1", status=TodoStatus.PENDING)]
        mock_todo_repo.get_all_for_user.return_value = mock_todos

        # Act
        result = todo_service.get_todos_for_user(user_id=1, status="pending")

        # Assert
        assert len(result) == 1
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status="pending",
            tag_ids=None,
            limit=50,
            offset=0,
        )

    def test_get_todos_with_invalid_status(self, todo_service, mock_todo_repo):
        """Test that invalid status raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            todo_service.get_todos_for_user(user_id=1, status="invalid_status")

        assert "Invalid status" in str(exc_info.value)
        mock_todo_repo.get_all_for_user.assert_not_called()

    def test_get_todos_with_tag_filter(self, todo_service, mock_todo_repo):
        """Test filtering TODOs by tags."""
        # Arrange
        mock_todos = [create_mock_todo(1, 1, "TODO 1")]
        mock_todo_repo.get_all_for_user.return_value = mock_todos

        # Act
        result = todo_service.get_todos_for_user(user_id=1, tag_ids=[1, 2])

        # Assert
        assert len(result) == 1
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status=None,
            tag_ids=[1, 2],
            limit=50,
            offset=0,
        )

    def test_get_todos_with_pagination(self, todo_service, mock_todo_repo):
        """Test pagination with limit and offset."""
        # Arrange
        mock_todos = [create_mock_todo(i, 1, f"TODO {i}") for i in range(10)]
        mock_todo_repo.get_all_for_user.return_value = mock_todos

        # Act
        result = todo_service.get_todos_for_user(
            user_id=1, limit=10, offset=20
        )

        # Assert
        assert len(result) == 10
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status=None,
            tag_ids=None,
            limit=10,
            offset=20,
        )

    def test_get_todos_limit_capped_at_100(self, todo_service, mock_todo_repo):
        """Test that limit is capped at 100."""
        # Arrange
        mock_todo_repo.get_all_for_user.return_value = []

        # Act
        todo_service.get_todos_for_user(user_id=1, limit=200)

        # Assert
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status=None,
            tag_ids=None,
            limit=100,  # Should be capped
            offset=0,
        )

    def test_get_todos_combined_filters(self, todo_service, mock_todo_repo):
        """Test combining status and tag filters with pagination."""
        # Arrange
        mock_todos = [create_mock_todo(1, 1, "TODO 1", status=TodoStatus.IN_PROGRESS)]
        mock_todo_repo.get_all_for_user.return_value = mock_todos

        # Act
        result = todo_service.get_todos_for_user(
            user_id=1,
            status="in_progress",
            tag_ids=[1],
            limit=25,
            offset=10,
        )

        # Assert
        assert len(result) == 1
        mock_todo_repo.get_all_for_user.assert_called_once_with(
            user_id=1,
            status="in_progress",
            tag_ids=[1],
            limit=25,
            offset=10,
        )

    def test_get_todos_empty_result(self, todo_service, mock_todo_repo):
        """Test that empty result is handled correctly."""
        # Arrange
        mock_todo_repo.get_all_for_user.return_value = []

        # Act
        result = todo_service.get_todos_for_user(user_id=1)

        # Assert
        assert result == []
        mock_todo_repo.get_all_for_user.assert_called_once()


class TestGetTodo:
    """Tests for get_todo method."""

    def test_get_todo_success(self, todo_service, mock_todo_repo):
        """Test getting a TODO by ID with valid authorization."""
        # Arrange
        mock_todo = create_mock_todo(1, 1, "Test TODO")
        mock_todo_repo.get_by_id.return_value = mock_todo

        # Act
        result = todo_service.get_todo(todo_id=1, user_id=1)

        # Assert
        assert result == mock_todo
        mock_todo_repo.get_by_id.assert_called_once_with(1)

    def test_get_todo_not_found(self, todo_service, mock_todo_repo):
        """Test that TodoNotFoundError is raised when TODO doesn't exist."""
        # Arrange
        mock_todo_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.get_todo(todo_id=999, user_id=1)

        assert "not found" in str(exc_info.value)
        mock_todo_repo.get_by_id.assert_called_once_with(999)

    def test_get_todo_unauthorized(self, todo_service, mock_todo_repo):
        """Test that UnauthorizedAccessError is raised for other user's TODO."""
        # Arrange
        mock_todo = create_mock_todo(1, 2, "Other user's TODO")  # user_id=2
        mock_todo_repo.get_by_id.return_value = mock_todo

        # Act & Assert
        with pytest.raises(UnauthorizedAccessError) as exc_info:
            todo_service.get_todo(todo_id=1, user_id=1)  # Requesting as user_id=1

        assert "permission" in str(exc_info.value).lower()
        mock_todo_repo.get_by_id.assert_called_once_with(1)


class TestCreateTodo:
    """Tests for create_todo method."""

    def test_create_todo_success(self, todo_service, mock_todo_repo):
        """Test creating a TODO successfully."""
        # Arrange
        mock_todo = create_mock_todo(1, 1, "New TODO")
        mock_todo_repo.create.return_value = mock_todo

        create_data = TodoCreate(
            title="New TODO",
            description="Description",
            status=TodoStatus.PENDING,
        )

        # Act
        result = todo_service.create_todo(user_id=1, data=create_data)

        # Assert
        assert result == mock_todo
        mock_todo_repo.create.assert_called_once()
        call_args = mock_todo_repo.create.call_args[1]
        assert call_args["user_id"] == 1
        assert call_args["title"] == "New TODO"
        assert call_args["description"] == "Description"


class TestUpdateTodo:
    """Tests for update_todo method."""

    def test_update_todo_success(self, todo_service, mock_todo_repo):
        """Test updating a TODO successfully."""
        # Arrange
        mock_todo = create_mock_todo(1, 1, "Original Title")
        updated_todo = create_mock_todo(1, 1, "Updated Title")
        mock_todo_repo.get_by_id.return_value = mock_todo
        mock_todo_repo.update.return_value = updated_todo

        update_data = TodoUpdate(title="Updated Title")

        # Act
        result = todo_service.update_todo(todo_id=1, user_id=1, data=update_data)

        # Assert
        assert result == updated_todo
        mock_todo_repo.get_by_id.assert_called_once_with(1)
        mock_todo_repo.update.assert_called_once()


class TestDeleteTodo:
    """Tests for delete_todo method."""

    def test_delete_todo_success(self, todo_service, mock_todo_repo):
        """Test deleting a TODO successfully."""
        # Arrange
        mock_todo = create_mock_todo(1, 1, "TODO to delete")
        mock_todo_repo.get_by_id.return_value = mock_todo

        # Act
        todo_service.delete_todo(todo_id=1, user_id=1)

        # Assert
        mock_todo_repo.get_by_id.assert_called_once_with(1)
        mock_todo_repo.delete.assert_called_once_with(mock_todo)

    def test_delete_todo_unauthorized(self, todo_service, mock_todo_repo):
        """Test that unauthorized user cannot delete TODO."""
        # Arrange
        mock_todo = create_mock_todo(1, 2, "Other user's TODO")
        mock_todo_repo.get_by_id.return_value = mock_todo

        # Act & Assert
        with pytest.raises(UnauthorizedAccessError):
            todo_service.delete_todo(todo_id=1, user_id=1)

        mock_todo_repo.delete.assert_not_called()
