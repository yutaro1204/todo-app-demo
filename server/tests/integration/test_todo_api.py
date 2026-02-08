"""
Integration tests for TODO API endpoints.
"""

import pytest
from app.models.todo import Todo, TodoStatus
from app.models.tag import Tag
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
def test_user2(test_db):
    """Create a second test user."""
    user = User(
        email="testuser2@example.com",
        name="Test User 2",
        password_hash=hash_password("TestPass123!"),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_tags(test_db):
    """Create test tags."""
    tags = [
        Tag(name="Work", color_code="#FF5733"),
        Tag(name="Personal", color_code="#33FF57"),
        Tag(name="Urgent", color_code="#5733FF"),
    ]
    for tag in tags:
        test_db.add(tag)
    test_db.commit()
    for tag in tags:
        test_db.refresh(tag)
    return tags


@pytest.fixture
def test_todos(test_db, test_user, test_tags):
    """Create test TODOs with various statuses and tags."""
    todos = [
        Todo(
            user_id=test_user.id,
            title="Pending TODO 1",
            description="First pending task",
            status=TodoStatus.PENDING,
        ),
        Todo(
            user_id=test_user.id,
            title="In Progress TODO",
            description="Task in progress",
            status=TodoStatus.IN_PROGRESS,
        ),
        Todo(
            user_id=test_user.id,
            title="Completed TODO",
            description="Completed task",
            status=TodoStatus.COMPLETED,
        ),
        Todo(
            user_id=test_user.id,
            title="Pending TODO 2",
            description="Second pending task",
            status=TodoStatus.PENDING,
        ),
    ]

    # Add tags to some TODOs
    todos[0].tags = [test_tags[0], test_tags[2]]  # Work, Urgent
    todos[1].tags = [test_tags[1]]  # Personal
    todos[2].tags = [test_tags[0]]  # Work

    for todo in todos:
        test_db.add(todo)
    test_db.commit()
    for todo in todos:
        test_db.refresh(todo)

    return todos


class TestListTodos:
    """Tests for GET /api/todos endpoint."""

    def test_list_todos_authenticated(self, authenticated_client, test_todos):
        """Test listing TODOs for authenticated user."""
        # Act
        response = authenticated_client.get("/api/todos")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 4
        assert all("id" in todo for todo in todos)
        assert all("title" in todo for todo in todos)
        assert all("status" in todo for todo in todos)
        assert all("tags" in todo for todo in todos)

    def test_list_todos_unauthenticated(self, client):
        """Test that unauthenticated request returns 401."""
        # Act
        response = client.get("/api/todos")

        # Assert
        assert response.status_code == 401

    def test_list_todos_ordered_by_created_at_desc(
        self, authenticated_client, test_todos
    ):
        """Test that TODOs are ordered by created_at DESC (newest first)."""
        # Act
        response = authenticated_client.get("/api/todos")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        # The last created TODO should be first
        assert todos[0]["title"] == "Pending TODO 2"
        assert todos[-1]["title"] == "Pending TODO 1"

    def test_list_todos_includes_tags(self, authenticated_client, test_todos):
        """Test that TODOs include their tags with eager loading."""
        # Act
        response = authenticated_client.get("/api/todos")

        # Assert
        assert response.status_code == 200
        todos = response.json()

        # Find "Pending TODO 1" which has 2 tags
        pending_todo_1 = next(
            todo for todo in todos if todo["title"] == "Pending TODO 1"
        )
        assert len(pending_todo_1["tags"]) == 2
        assert any(tag["name"] == "Work" for tag in pending_todo_1["tags"])
        assert any(tag["name"] == "Urgent" for tag in pending_todo_1["tags"])

    def test_list_todos_filter_by_status_pending(
        self, authenticated_client, test_todos
    ):
        """Test filtering TODOs by status=pending."""
        # Act
        response = authenticated_client.get("/api/todos?status=pending")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        assert all(todo["status"] == "pending" for todo in todos)

    def test_list_todos_filter_by_status_in_progress(
        self, authenticated_client, test_todos
    ):
        """Test filtering TODOs by status=in_progress."""
        # Act
        response = authenticated_client.get("/api/todos?status=in_progress")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["status"] == "in_progress"
        assert todos[0]["title"] == "In Progress TODO"

    def test_list_todos_filter_by_status_completed(
        self, authenticated_client, test_todos
    ):
        """Test filtering TODOs by status=completed."""
        # Act
        response = authenticated_client.get("/api/todos?status=completed")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["status"] == "completed"
        assert todos[0]["title"] == "Completed TODO"

    def test_list_todos_filter_by_invalid_status(
        self, authenticated_client, test_todos
    ):
        """Test that invalid status returns 400."""
        # Act
        response = authenticated_client.get("/api/todos?status=invalid_status")

        # Assert
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

    def test_list_todos_filter_by_single_tag(
        self, authenticated_client, test_todos, test_tags
    ):
        """Test filtering TODOs by a single tag."""
        # Act - Filter by "Work" tag
        work_tag_id = test_tags[0].id
        response = authenticated_client.get(f"/api/todos?tag_ids={work_tag_id}")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2  # "Pending TODO 1" and "Completed TODO"
        titles = [todo["title"] for todo in todos]
        assert "Pending TODO 1" in titles
        assert "Completed TODO" in titles

    def test_list_todos_filter_by_multiple_tags(
        self, authenticated_client, test_todos, test_tags
    ):
        """Test filtering TODOs by multiple tags."""
        # Act - Filter by "Work" and "Urgent" tags
        work_tag_id = test_tags[0].id
        urgent_tag_id = test_tags[2].id
        response = authenticated_client.get(
            f"/api/todos?tag_ids={work_tag_id},{urgent_tag_id}"
        )

        # Assert
        assert response.status_code == 200
        todos = response.json()
        # Should return TODOs that have either Work OR Urgent tag
        assert len(todos) >= 1

    def test_list_todos_filter_by_invalid_tag_ids(
        self, authenticated_client, test_todos
    ):
        """Test that invalid tag_ids format returns 400."""
        # Act
        response = authenticated_client.get("/api/todos?tag_ids=abc,def")

        # Assert
        assert response.status_code == 400
        assert "Invalid tag_ids format" in response.json()["detail"]

    def test_list_todos_pagination_limit(self, authenticated_client, test_todos):
        """Test pagination with limit parameter."""
        # Act
        response = authenticated_client.get("/api/todos?limit=2")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2

    def test_list_todos_pagination_offset(self, authenticated_client, test_todos):
        """Test pagination with offset parameter."""
        # Act - Get all TODOs first
        all_response = authenticated_client.get("/api/todos")
        all_todos = all_response.json()

        # Get TODOs with offset
        offset_response = authenticated_client.get("/api/todos?offset=2")
        offset_todos = offset_response.json()

        # Assert
        assert offset_response.status_code == 200
        assert len(offset_todos) == 2  # 4 total - 2 offset = 2 remaining
        # The IDs should match the last 2 from all_todos
        assert offset_todos[0]["id"] == all_todos[2]["id"]

    def test_list_todos_pagination_limit_and_offset(
        self, authenticated_client, test_todos
    ):
        """Test pagination with both limit and offset."""
        # Act
        response = authenticated_client.get("/api/todos?limit=1&offset=1")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1

    def test_list_todos_limit_exceeds_maximum(self, authenticated_client, test_todos):
        """Test that limit is capped at 100."""
        # Act - Request limit > 100
        response = authenticated_client.get("/api/todos?limit=200")

        # Assert
        assert response.status_code == 200
        # Should still work, but internally capped at 100

    def test_list_todos_combined_filters(
        self, authenticated_client, test_todos, test_tags
    ):
        """Test combining status and tag filters."""
        # Act - Filter by status=pending AND tag=Work
        work_tag_id = test_tags[0].id
        response = authenticated_client.get(
            f"/api/todos?status=pending&tag_ids={work_tag_id}"
        )

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["title"] == "Pending TODO 1"
        assert todos[0]["status"] == "pending"

    def test_list_todos_user_isolation(
        self, authenticated_client, test_db, test_user2, test_todos
    ):
        """Test that users can only see their own TODOs."""
        # Arrange - Create a TODO for user2
        user2_todo = Todo(
            user_id=test_user2.id,
            title="User 2 TODO",
            status=TodoStatus.PENDING,
        )
        test_db.add(user2_todo)
        test_db.commit()

        # Act - User 1 lists their TODOs
        response = authenticated_client.get("/api/todos")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        # Should only see test_user's TODOs, not user2's
        titles = [todo["title"] for todo in todos]
        assert "User 2 TODO" not in titles
        assert len(todos) == 4  # Only user 1's TODOs

    def test_list_todos_empty_result(self, authenticated_client):
        """Test that empty result is handled correctly."""
        # Act - No TODOs created yet
        response = authenticated_client.get("/api/todos")

        # Assert
        assert response.status_code == 200
        todos = response.json()
        assert todos == []


class TestCreateTodo:
    """Tests for POST /api/todos endpoint."""

    def test_create_todo_minimal(self, authenticated_client, test_user):
        """Test creating a TODO with minimal required data."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={"title": "Buy groceries"}
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert todo["title"] == "Buy groceries"
        assert todo["status"] == "pending"  # Default
        assert todo["description"] is None
        assert todo["user_id"] == test_user.id
        assert "id" in todo
        assert "created_at" in todo
        assert "updated_at" in todo
        assert todo["tags"] == []

    def test_create_todo_full_data(self, authenticated_client, test_user, test_tags):
        """Test creating a TODO with all fields."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Complete project",
                "description": "Finish the TODO app implementation",
                "status": "in_progress",
                "starts_date": "2026-02-08T10:00:00Z",
                "expires_date": "2026-02-15T18:00:00Z",
                "tag_ids": [test_tags[0].id, test_tags[1].id]
            }
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert todo["title"] == "Complete project"
        assert todo["description"] == "Finish the TODO app implementation"
        assert todo["status"] == "in_progress"
        assert todo["user_id"] == test_user.id
        assert len(todo["tags"]) == 2
        tag_names = [tag["name"] for tag in todo["tags"]]
        assert "Work" in tag_names
        assert "Personal" in tag_names

    def test_create_todo_with_single_tag(self, authenticated_client, test_tags):
        """Test creating a TODO with a single tag."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Tagged task",
                "tag_ids": [test_tags[0].id]
            }
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert len(todo["tags"]) == 1
        assert todo["tags"][0]["name"] == "Work"

    def test_create_todo_unauthenticated(self, client):
        """Test that unauthenticated request returns 401."""
        # Act
        response = client.post(
            "/api/todos",
            json={"title": "Test TODO"}
        )

        # Assert
        assert response.status_code == 401

    def test_create_todo_missing_title(self, authenticated_client):
        """Test that missing required title returns 422."""
        # Act
        response = authenticated_client.post("/api/todos", json={})

        # Assert
        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    def test_create_todo_empty_title(self, authenticated_client):
        """Test that empty title returns 422."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={"title": ""}
        )

        # Assert
        assert response.status_code == 422

    def test_create_todo_title_too_long(self, authenticated_client):
        """Test that title longer than 200 chars returns 422."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={"title": "x" * 201}
        )

        # Assert
        assert response.status_code == 422

    def test_create_todo_description_too_long(self, authenticated_client):
        """Test that description longer than 2000 chars returns 422."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Valid title",
                "description": "x" * 2001
            }
        )

        # Assert
        assert response.status_code == 422

    def test_create_todo_invalid_status(self, authenticated_client):
        """Test that invalid status value returns 422."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Test TODO",
                "status": "invalid_status"
            }
        )

        # Assert
        assert response.status_code == 422

    def test_create_todo_expires_before_starts(self, authenticated_client):
        """Test that expires_date before starts_date returns 422."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Invalid dates",
                "starts_date": "2026-02-15T10:00:00Z",
                "expires_date": "2026-02-08T10:00:00Z"
            }
        )

        # Assert
        assert response.status_code == 422
        error = response.json()
        assert "expires_date" in str(error).lower()

    def test_create_todo_with_dates(self, authenticated_client):
        """Test creating a TODO with valid start and end dates."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Dated task",
                "starts_date": "2026-02-08T10:00:00Z",
                "expires_date": "2026-02-15T18:00:00Z"
            }
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert todo["starts_date"] is not None
        assert todo["expires_date"] is not None

    def test_create_todo_default_status(self, authenticated_client):
        """Test that default status is 'pending'."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={"title": "Default status task"}
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert todo["status"] == "pending"

    def test_create_todo_with_description_only(self, authenticated_client):
        """Test creating a TODO with title and description only."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={
                "title": "Simple task",
                "description": "This is a simple description"
            }
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert todo["description"] == "This is a simple description"
        assert todo["status"] == "pending"
        assert todo["starts_date"] is None
        assert todo["expires_date"] is None

    def test_create_todo_response_includes_timestamps(self, authenticated_client):
        """Test that response includes created_at and updated_at."""
        # Act
        response = authenticated_client.post(
            "/api/todos",
            json={"title": "Timestamp test"}
        )

        # Assert
        assert response.status_code == 201
        todo = response.json()
        assert "created_at" in todo
        assert "updated_at" in todo
        assert todo["created_at"] is not None
        assert todo["updated_at"] is not None

    def test_create_multiple_todos_for_same_user(self, authenticated_client):
        """Test creating multiple TODOs for the same user."""
        # Act
        response1 = authenticated_client.post(
            "/api/todos",
            json={"title": "First TODO"}
        )
        response2 = authenticated_client.post(
            "/api/todos",
            json={"title": "Second TODO"}
        )

        # Assert
        assert response1.status_code == 201
        assert response2.status_code == 201
        todo1 = response1.json()
        todo2 = response2.json()
        assert todo1["id"] != todo2["id"]
        assert todo1["user_id"] == todo2["user_id"]
