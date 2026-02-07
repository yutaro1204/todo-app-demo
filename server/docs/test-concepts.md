# Test Concepts

This document explains the differences between unit tests, integration tests, and E2E tests, and provides guidance on building a comprehensive testing strategy for the FastAPI/Python TODO app server.

## Testing Types Overview

### 🔬 Unit Tests

**Scope**: Test individual units of code in isolation (functions, methods, classes)

**Characteristics**:

- **Fastest** to run (milliseconds)
- **Cheapest** to maintain
- **Most isolated** - mock all dependencies
- **Most granular** - test specific logic
- **Easy to debug** - failure points to exact issue

**Example for TODO app server**:

```python
# tests/unit/test_utils.py
from app.utils.datetime_utils import is_expired, days_until
from datetime import datetime, timedelta

def test_is_expired_returns_true_for_past_date():
    """Test that past dates are identified as expired."""
    past_date = datetime.utcnow() - timedelta(days=1)
    assert is_expired(past_date) is True

def test_is_expired_returns_false_for_future_date():
    """Test that future dates are not expired."""
    future_date = datetime.utcnow() + timedelta(days=1)
    assert is_expired(future_date) is False

def test_days_until_calculates_correctly():
    """Test days until calculation."""
    target = datetime.utcnow() + timedelta(days=5)
    assert days_until(target) == 5

# tests/unit/test_validators.py
import pytest
from pydantic import ValidationError
from app.schemas.todo import TodoCreate

def test_todo_title_must_not_be_empty():
    """Test that empty titles are rejected."""
    with pytest.raises(ValidationError):
        TodoCreate(title="")

def test_expires_date_must_be_after_starts_date():
    """Test date validation logic."""
    from datetime import datetime, timedelta

    starts = datetime.utcnow()
    expires = starts - timedelta(days=1)

    with pytest.raises(ValidationError) as exc_info:
        TodoCreate(
            title="Test",
            starts_date=starts,
            expires_date=expires
        )
    assert "expires_date must be after starts_date" in str(exc_info.value)
```

**What to test**:

- Pure functions (formatting, calculations, date utilities)
- Pydantic schema validation logic
- Business rule validation
- Data transformations
- Password hashing utilities
- Helper functions

---

### 🔗 Integration Tests

**Scope**: Test how multiple units work together with real dependencies (database, external services)

**Characteristics**:

- **Moderate speed** (seconds to minutes)
- **Moderate cost** to maintain
- **Real dependencies** - use actual PostgreSQL database
- **Controlled environment** - test database isolated from development
- **Tests full stack** - from API endpoint to database and back
- **More realistic** than unit tests, more controlled than E2E tests

**FastAPI Testing Approach**:

Integration tests for FastAPI applications test:

1. **API Endpoint Tests** - Test routes with real database:
   - HTTP request → FastAPI router → Service → Repository → PostgreSQL
   - Validates request/response handling
   - Verifies database state changes
   - Tests authentication and authorization
   - Validates error handling

2. **Service Layer Tests** - Test business logic with real repository:
   - Tests services with real database access
   - Validates complex business rules
   - Tests transaction handling

**Environment Setup**:

```python
# tests/conftest.py - Test fixtures
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.models import user, todo, tag  # Import all models

# Test database (SQLite for speed, or PostgreSQL for parity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# Or use PostgreSQL test database:
# SQLALCHEMY_DATABASE_URL = "postgresql://todoapp:test@localhost:5432/todoapp_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client(client, test_db):
    """Test client with authenticated user."""
    # Create test user
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("testpass123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Sign in
    response = client.post("/api/auth/signin", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = response.json()["token"]

    # Add token to client headers
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
```

**Example Integration Tests**:

```python
# tests/integration/test_auth_api.py
from fastapi.testclient import TestClient
from app.models.user import User

def test_signup_creates_user(client, test_db):
    """Test user registration creates database record."""
    response = client.post("/api/auth/signup", json={
        "email": "newuser@example.com",
        "name": "New User",
        "password": "securepass123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data

    # Verify in database
    user = test_db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.name == "New User"
    # Password should be hashed, not plain
    assert user.password_hash != "securepass123"

def test_signup_rejects_duplicate_email(client, test_db):
    """Test that duplicate emails are rejected."""
    # Create first user
    client.post("/api/auth/signup", json={
        "email": "duplicate@example.com",
        "name": "User One",
        "password": "pass123"
    })

    # Try to create second user with same email
    response = client.post("/api/auth/signup", json={
        "email": "duplicate@example.com",
        "name": "User Two",
        "password": "pass456"
    })

    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"].lower()

def test_signin_returns_token(client, test_db):
    """Test successful sign in returns authentication token."""
    # Create user
    client.post("/api/auth/signup", json={
        "email": "signin@example.com",
        "name": "Sign In User",
        "password": "testpass123"
    })

    # Sign in
    response = client.post("/api/auth/signin", json={
        "email": "signin@example.com",
        "password": "testpass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "signin@example.com"

def test_signin_rejects_invalid_password(client, test_db):
    """Test that invalid passwords are rejected."""
    # Create user
    client.post("/api/auth/signup", json={
        "email": "user@example.com",
        "name": "User",
        "password": "correctpass"
    })

    # Try to sign in with wrong password
    response = client.post("/api/auth/signin", json={
        "email": "user@example.com",
        "password": "wrongpass"
    })

    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


# tests/integration/test_todo_api.py
def test_create_todo_integration(authenticated_client, test_db):
    """Test TODO creation with real database."""
    response = authenticated_client.post("/api/todos", json={
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "status": "pending"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["status"] == "pending"
    assert "id" in data

    # Verify in database
    from app.models.todo import Todo
    todo = test_db.query(Todo).filter(Todo.id == data["id"]).first()
    assert todo is not None
    assert todo.title == "Buy groceries"

def test_get_todos_returns_only_user_todos(authenticated_client, test_db):
    """Test that users only see their own TODOs."""
    # Create TODO for authenticated user
    response1 = authenticated_client.post("/api/todos", json={
        "title": "My TODO",
        "status": "pending"
    })
    my_todo_id = response1.json()["id"]

    # Create another user and their TODO
    from app.models.user import User
    from app.models.todo import Todo
    from app.core.security import hash_password

    other_user = User(
        email="other@example.com",
        name="Other User",
        password_hash=hash_password("pass123")
    )
    test_db.add(other_user)
    test_db.commit()
    test_db.refresh(other_user)

    other_todo = Todo(
        user_id=other_user.id,
        title="Other's TODO",
        status="pending"
    )
    test_db.add(other_todo)
    test_db.commit()

    # Get TODOs for authenticated user
    response = authenticated_client.get("/api/todos")
    assert response.status_code == 200

    todos = response.json()
    todo_ids = [t["id"] for t in todos]

    # Should include own TODO
    assert my_todo_id in todo_ids
    # Should NOT include other user's TODO
    assert other_todo.id not in todo_ids

def test_update_todo_integration(authenticated_client, test_db):
    """Test TODO update with database persistence."""
    # Create TODO
    response = authenticated_client.post("/api/todos", json={
        "title": "Original Title",
        "status": "pending"
    })
    todo_id = response.json()["id"]

    # Update TODO
    response = authenticated_client.put(f"/api/todos/{todo_id}", json={
        "title": "Updated Title",
        "status": "completed"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"

    # Verify in database
    from app.models.todo import Todo
    todo = test_db.query(Todo).filter(Todo.id == todo_id).first()
    assert todo.title == "Updated Title"
    assert todo.status == "completed"

def test_delete_todo_integration(authenticated_client, test_db):
    """Test TODO deletion removes from database."""
    # Create TODO
    response = authenticated_client.post("/api/todos", json={
        "title": "To be deleted",
        "status": "pending"
    })
    todo_id = response.json()["id"]

    # Delete TODO
    response = authenticated_client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 200

    # Verify deleted from database
    from app.models.todo import Todo
    todo = test_db.query(Todo).filter(Todo.id == todo_id).first()
    assert todo is None

def test_unauthorized_user_cannot_access_others_todos(client, test_db):
    """Test authorization prevents accessing other users' TODOs."""
    from app.models.user import User
    from app.models.todo import Todo
    from app.core.security import hash_password

    # Create two users
    user1 = User(email="user1@example.com", name="User 1",
                 password_hash=hash_password("pass1"))
    user2 = User(email="user2@example.com", name="User 2",
                 password_hash=hash_password("pass2"))
    test_db.add_all([user1, user2])
    test_db.commit()
    test_db.refresh(user1)
    test_db.refresh(user2)

    # Create TODO for user1
    todo = Todo(user_id=user1.id, title="User 1's TODO", status="pending")
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)

    # Sign in as user2
    response = client.post("/api/auth/signin", json={
        "email": "user2@example.com",
        "password": "pass2"
    })
    token = response.json()["token"]

    # Try to access user1's TODO as user2
    response = client.get(
        f"/api/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403  # Forbidden
```

**What to test**:

- API endpoints with real database operations
- Authentication and authorization flows
- CRUD operations (Create, Read, Update, Delete)
- Database queries with filters and pagination
- Transaction handling and rollback
- Error scenarios (404, 403, 400)
- Password verification and hashing

**Running Integration Tests**:

```bash
# Run all tests
pytest

# Run only integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_todo_api.py -v

# Run specific test
pytest tests/integration/test_todo_api.py::test_create_todo_integration -v
```

---

### 🌐 E2E (End-to-End) Tests

**Scope**: Test complete user journeys through the entire application from client to server to database

**Characteristics**:

- **Slowest** to run (minutes to hours)
- **Most expensive** to maintain
- **No mocking** - tests real system with all components
- **Tests user flows** - complete workflows from user's perspective
- **Requires full system** - frontend + backend + database
- **Production-like environment** - deployed or staging environment

**For the TODO App Server**:

E2E tests would require:

1. **Frontend Application**: The client app that calls the API
2. **Backend Server**: This FastAPI server running
3. **Database**: PostgreSQL with test data
4. **Browser Automation**: Tool like Playwright, Selenium, or Cypress

**Example E2E Test Flow** (if you had a frontend):

```python
# tests/e2e/test_user_journey.py
# This would use Playwright or Selenium

from playwright.sync_api import sync_playwright

def test_complete_todo_workflow():
    """
    Test complete user journey:
    1. Sign up
    2. Sign in
    3. Create TODO
    4. View TODO list
    5. Update TODO
    6. Delete TODO
    7. Sign out
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to app
        page.goto("http://localhost:3000")

        # Sign up
        page.click("text=Sign Up")
        page.fill("input[name=email]", "e2e@example.com")
        page.fill("input[name=password]", "testpass123")
        page.fill("input[name=name]", "E2E User")
        page.click("button:has-text('Create Account')")

        # Should redirect to dashboard
        page.wait_for_url("**/dashboard")

        # Create TODO
        page.click("text=New TODO")
        page.fill("input[name=title]", "E2E Test TODO")
        page.fill("textarea[name=description]", "Created by E2E test")
        page.click("button:has-text('Save')")

        # Verify TODO appears in list
        page.wait_for_selector("text=E2E Test TODO")

        # Update TODO
        page.click("text=E2E Test TODO")
        page.click("button:has-text('Edit')")
        page.fill("input[name=title]", "Updated E2E TODO")
        page.select_option("select[name=status]", "completed")
        page.click("button:has-text('Save')")

        # Verify update
        page.wait_for_selector("text=Updated E2E TODO")
        page.wait_for_selector("text=completed")

        # Delete TODO
        page.click("button:has-text('Delete')")
        page.click("button:has-text('Confirm')")

        # Verify deletion
        assert page.query_selector("text=Updated E2E TODO") is None

        # Sign out
        page.click("button:has-text('Sign Out')")
        page.wait_for_url("**/signin")

        browser.close()
```

**What to test in E2E**:

- Complete user workflows
- Frontend-backend integration
- Authentication across full stack
- Error handling visible to users
- Browser compatibility
- Mobile responsiveness

**Note**: Since this is a backend-only project, E2E tests would require the frontend application to be developed first.

---

## Testing Pyramid

The testing pyramid guides test distribution:

```
        /\
       /  \
      / E2E \        ← Few (5-10%)
     /______\
    /        \
   / Integration \   ← Some (20-30%)
  /______________\
 /                \
/   Unit Tests     \  ← Many (60-75%)
/____________________\
```

**For TODO App Server:**

- **60-75% Unit Tests**: Fast, isolated tests of utilities, validators, schemas
- **20-30% Integration Tests**: API endpoints with real database
- **5-10% E2E Tests**: Full user journeys (would require frontend)

---

## Testing Best Practices

### 1. Test Naming

```python
# Good - descriptive test names
def test_user_cannot_update_other_users_todo():
    """Test authorization prevents unauthorized updates."""
    pass

def test_expired_session_returns_401():
    """Test that expired sessions are rejected."""
    pass

# Avoid - vague test names
def test_todo():
    pass

def test_1():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_create_todo_with_tags(authenticated_client, test_db):
    # Arrange - set up test data
    from app.models.tag import Tag
    tag = Tag(name="work", color_code="#FF5733")
    test_db.add(tag)
    test_db.commit()
    test_db.refresh(tag)

    # Act - perform the action
    response = authenticated_client.post("/api/todos", json={
        "title": "TODO with tag",
        "tag_ids": [tag.id]
    })

    # Assert - verify the result
    assert response.status_code == 201
    data = response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "work"
```

### 3. Use Fixtures for Common Setup

```python
# tests/conftest.py
@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        email="sample@example.com",
        name="Sample User",
        password_hash=hash_password("samplepass")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def sample_todo(test_db, sample_user):
    """Create a sample TODO for testing."""
    from app.models.todo import Todo

    todo = Todo(
        user_id=sample_user.id,
        title="Sample TODO",
        status="pending"
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    return todo
```

### 4. Test Edge Cases

```python
def test_todo_with_maximum_length_title(authenticated_client):
    """Test TODO creation with max length title."""
    max_title = "A" * 200  # Maximum allowed length

    response = authenticated_client.post("/api/todos", json={
        "title": max_title,
        "status": "pending"
    })

    assert response.status_code == 201
    assert response.json()["title"] == max_title

def test_todo_title_exceeds_maximum_length(authenticated_client):
    """Test that titles exceeding max length are rejected."""
    too_long_title = "A" * 201  # One character over limit

    response = authenticated_client.post("/api/todos", json={
        "title": too_long_title,
        "status": "pending"
    })

    assert response.status_code == 422  # Validation error
```

### 5. Test Error Scenarios

```python
def test_get_nonexistent_todo_returns_404(authenticated_client):
    """Test that accessing non-existent TODO returns 404."""
    response = authenticated_client.get("/api/todos/99999")
    assert response.status_code == 404

def test_create_todo_without_title_returns_422(authenticated_client):
    """Test that missing required field returns validation error."""
    response = authenticated_client.post("/api/todos", json={
        "description": "No title provided",
        "status": "pending"
    })
    assert response.status_code == 422
```

---

## Test Coverage Goals

### Coverage Targets

- **Overall Coverage**: > 80%
- **Critical Business Logic**: > 90%
- **API Endpoints**: 100%
- **Authentication/Authorization**: 100%

### Measuring Coverage

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # Opens in browser

# Check coverage percentage
pytest --cov=app --cov-report=term-missing
```

### Coverage Configuration

```ini
# .coveragerc or setup.cfg
[coverage:run]
source = app
omit =
    app/__init__.py
    app/main.py
    */tests/*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: todoapp
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: todoapp_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://todoapp:testpass@localhost:5432/todoapp_test
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Testing Checklist

### Before Committing

- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Coverage hasn't decreased
- [ ] No skipped or marked tests without reason

### Test Quality

- [ ] Tests are isolated (no dependencies between tests)
- [ ] Tests are deterministic (same result every time)
- [ ] Tests have clear, descriptive names
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Edge cases are covered
- [ ] Error scenarios are tested
- [ ] Tests run quickly

---

## Summary

**Test Distribution for TODO App Server:**

- **Unit Tests (60-75%)**: Test utilities, validators, Pydantic schemas, business logic
- **Integration Tests (20-30%)**: Test API endpoints with real PostgreSQL database
- **E2E Tests (5-10%)**: Would test complete user flows (requires frontend)

**Key Principles:**

1. Write tests first (TDD) or immediately after code
2. Keep tests fast and isolated
3. Use real database for integration tests
4. Mock external services, not internal code
5. Aim for high coverage of critical paths
6. Test behavior, not implementation
7. Make tests readable and maintainable
