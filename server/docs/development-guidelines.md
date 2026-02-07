# Development Guidelines

## Coding Manner

### FastAPI Patterns

This project follows FastAPI conventions and best practices. Key patterns to follow:

#### API Route Handlers

```python
# Good - clear dependency injection, type hints, response model
from fastapi import APIRouter, Depends, status
from app.schemas.todo import TodoCreate, TodoResponse
from app.services.todo_service import TodoService
from app.api.deps import get_current_user, get_todo_service

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    """Create a new TODO for the authenticated user."""
    return await todo_service.create_todo(current_user.id, todo_data)

# Include error handling
from fastapi import HTTPException

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    todo = await todo_service.get_todo(todo_id, current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO not found"
        )
    return todo
```

#### Dependency Injection

```python
# Good - reusable dependencies
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.repositories.todo_repository import TodoRepository
from app.services.todo_service import TodoService

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_todo_repository(db: Session = Depends(get_db)) -> TodoRepository:
    """Todo repository dependency."""
    return TodoRepository(db)

def get_todo_service(
    todo_repo: TodoRepository = Depends(get_todo_repository)
) -> TodoService:
    """Todo service dependency."""
    return TodoService(todo_repo)
```

#### Async Endpoints

```python
# Use async for I/O-bound operations
@router.get("/todos")
async def get_todos(
    db: Session = Depends(get_db)
):
    # Async database operations
    return await fetch_todos_from_db(db)

# Use sync for CPU-bound operations
@router.post("/compute")
def compute_result(data: ComputeRequest):
    # Synchronous computation
    return perform_heavy_computation(data)
```

### Repository Pattern

```python
# Good - repository encapsulates database access
from sqlalchemy.orm import Session
from app.models.todo import Todo
from typing import Optional

class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """Get a single TODO by ID."""
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def get_all_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Todo]:
        """Get all TODOs for a user with pagination."""
        return self.db.query(Todo)\
            .filter(Todo.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create(self, user_id: int, **kwargs) -> Todo:
        """Create a new TODO."""
        todo = Todo(user_id=user_id, **kwargs)
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo
```

### Service Layer Pattern

```python
# Good - service contains business logic
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import TodoCreate
from app.models.todo import Todo
from fastapi import HTTPException, status

class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def create_todo(self, user_id: int, data: TodoCreate) -> Todo:
        """Create a TODO with business logic validation."""
        # Business rule: expires_date must be after starts_date
        if data.expires_date and data.starts_date:
            if data.expires_date < data.starts_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="expires_date must be after starts_date"
                )

        return self.todo_repo.create(
            user_id=user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            starts_date=data.starts_date,
            expires_date=data.expires_date
        )

    async def get_todo(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """Get TODO with authorization check."""
        todo = self.todo_repo.get_by_id(todo_id)
        if todo and todo.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this TODO"
            )
        return todo
```

## Python Best Practices

### Type Hints

```python
# Good - comprehensive type hints
from typing import Optional, List
from datetime import datetime

def get_user_todos(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Todo]:
    """Retrieve user's TODOs with optional filtering."""
    pass

# Use type aliases for complex types
from typing import Dict, Any

TodoDict = Dict[str, Any]

def serialize_todo(todo: Todo) -> TodoDict:
    """Convert TODO model to dictionary."""
    return {
        "id": todo.id,
        "title": todo.title,
        "status": todo.status
    }

# Use | for union types (Python 3.10+)
def get_todo(todo_id: int) -> Todo | None:
    """Get TODO by ID, returns None if not found."""
    pass
```

### Error Handling

```python
# Good - specific exception handling
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Custom exceptions
class TodoNotFoundError(Exception):
    """Raised when TODO is not found."""
    pass

class UnauthorizedAccessError(Exception):
    """Raised when user tries to access unauthorized resource."""
    pass

# Exception handler registration
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )
```

## Validation with Pydantic

This project uses Pydantic for request validation and response serialization.

### Defining Schemas

```python
# app/schemas/todo.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoCreate(BaseModel):
    """Schema for creating a TODO."""
    title: str = Field(..., min_length=1, max_length=200, description="TODO title")
    description: str | None = Field(None, max_length=2000, description="Detailed description")
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @field_validator('expires_date')
    @classmethod
    def expires_must_be_future(cls, v: datetime | None, info) -> datetime | None:
        """Ensure expires_date is in the future."""
        if v and v < datetime.utcnow():
            raise ValueError('expires_date must be in the future')
        if v and info.data.get('starts_date') and v < info.data['starts_date']:
            raise ValueError('expires_date must be after starts_date')
        return v

class TodoUpdate(BaseModel):
    """Schema for updating a TODO."""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TodoStatus | None = None
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] | None = None

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

    class Config:
        from_attributes = True  # Enable ORM model conversion
```

### Using Schemas in Endpoints

```python
@router.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,  # Automatic validation
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """Pydantic automatically validates todo_data."""
    return await todo_service.create_todo(current_user.id, todo_data)

@router.get("/todos", response_model=list[TodoResponse])
async def get_todos(
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """Response automatically serialized to TodoResponse format."""
    todos = await todo_service.get_user_todos(current_user.id)
    return todos
```

### Reusable Validation

```python
# app/schemas/common.py
from pydantic import BaseModel, EmailStr, field_validator
import re

class EmailField(BaseModel):
    """Reusable email validation."""
    email: EmailStr

def validate_hex_color(v: str) -> str:
    """Validate hex color code."""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
        raise ValueError('Must be a valid hex color code (e.g., #FF5733)')
    return v

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color_code: str

    @field_validator('color_code')
    @classmethod
    def validate_color(cls, v: str) -> str:
        return validate_hex_color(v)
```

## Naming Rules

### Variables and Functions

```python
# snake_case for variables and functions
user_id = 1
todo_list = []
session_token = "abc123"

def get_user_by_email(email: str) -> User | None:
    """Retrieve user by email address."""
    pass

def create_todo(user_id: int, title: str) -> Todo:
    """Create a new TODO."""
    pass

# Boolean variables prefixed with is/has/can/should
is_authenticated = True
has_permission = False
can_edit = True
should_notify = False
```

### Constants

```python
# UPPER_SNAKE_CASE for constants
MAX_TODO_TITLE_LENGTH = 200
DEFAULT_PAGE_SIZE = 50
SESSION_EXPIRE_MINUTES = 1440
BCRYPT_ROUNDS = 12

# Configuration constants from settings
API_PREFIX = "/api"
ALLOWED_ORIGINS = ["http://localhost:3000"]
```

### Classes

```python
# PascalCase for classes
class UserRepository:
    pass

class TodoService:
    pass

class TodoCreateSchema:
    pass

# Use descriptive names
# Good
class AuthenticationService:
    pass

# Avoid
class Auth:  # Too abbreviated
    pass
```

### Models

```python
# PascalCase, singular nouns
class User(Base):
    __tablename__ = "users"  # Plural table name

class Todo(Base):
    __tablename__ = "todos"

class Tag(Base):
    __tablename__ = "tags"
```

### Pydantic Schemas

```python
# PascalCase with suffix indicating purpose
class TodoCreate(BaseModel):
    """For creating TODOs."""
    pass

class TodoUpdate(BaseModel):
    """For updating TODOs."""
    pass

class TodoResponse(BaseModel):
    """For API responses."""
    pass

class TodoInDB(BaseModel):
    """Internal database representation."""
    pass
```

### Files and Directories

```python
# snake_case for modules and packages
app/
├── models/
│   ├── user.py          # Good
│   ├── todo.py          # Good
│   └── todo_tag.py      # Good (multi-word)
├── services/
│   ├── auth_service.py  # Good
│   └── todo_service.py  # Good
└── repositories/
    └── user_repository.py

# Avoid
app/
├── Models/              # Bad - PascalCase directory
├── userModel.py         # Bad - camelCase
└── TodoService.py       # Bad - PascalCase file
```

### Function Naming

```python
# Verbs for actions
def create_user(email: str, password: str) -> User:
    pass

def update_todo(todo_id: int, data: dict) -> Todo:
    pass

def delete_tag(tag_id: int) -> None:
    pass

# Getters
def get_user_by_id(user_id: int) -> User | None:
    pass

def get_todos_for_user(user_id: int) -> list[Todo]:
    pass

# Boolean functions
def is_authenticated(token: str) -> bool:
    pass

def has_permission(user: User, resource: str) -> bool:
    pass

def can_edit_todo(user: User, todo: Todo) -> bool:
    pass
```

## Database Operations

### SQLAlchemy Best Practices

```python
# Good - use context manager or explicit session handling
from sqlalchemy.orm import Session

def create_todo(db: Session, user_id: int, title: str) -> Todo:
    """Create TODO with proper session handling."""
    todo = Todo(user_id=user_id, title=title)
    db.add(todo)
    db.commit()
    db.refresh(todo)  # Get updated data from DB
    return todo

# Good - eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

def get_todos_with_tags(db: Session, user_id: int) -> list[Todo]:
    """Load TODOs with tags in single query."""
    return db.query(Todo)\
        .options(joinedload(Todo.tags))\
        .filter(Todo.user_id == user_id)\
        .all()

# Good - use exists() for checking existence
def user_exists(db: Session, email: str) -> bool:
    """Check if user exists efficiently."""
    return db.query(User).filter(User.email == email).first() is not None

# Better - more efficient
from sqlalchemy import exists, select

def user_exists(db: Session, email: str) -> bool:
    """Check if user exists with EXISTS query."""
    return db.query(exists().where(User.email == email)).scalar()

# Good - use transactions for multiple operations
def transfer_todos(db: Session, from_user: int, to_user: int):
    """Transfer TODOs between users atomically."""
    try:
        db.query(Todo)\
            .filter(Todo.user_id == from_user)\
            .update({"user_id": to_user})
        db.commit()
    except Exception:
        db.rollback()
        raise
```

### Query Optimization

```python
# Add indexes for frequently queried columns
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # Indexed
    status = Column(String, index=True)  # Indexed for filtering
    created_at = Column(DateTime, index=True)  # Indexed for sorting

# Use pagination for large result sets
def get_todos_paginated(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> list[Todo]:
    """Get paginated TODO list."""
    return db.query(Todo)\
        .filter(Todo.user_id == user_id)\
        .order_by(Todo.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

# Filter in database, not in Python
# Good - database filtering
def get_active_todos(db: Session, user_id: int) -> list[Todo]:
    return db.query(Todo)\
        .filter(
            Todo.user_id == user_id,
            Todo.status != "completed"
        )\
        .all()

# Avoid - filtering in Python
def get_active_todos(db: Session, user_id: int) -> list[Todo]:
    todos = db.query(Todo).filter(Todo.user_id == user_id).all()
    return [t for t in todos if t.status != "completed"]  # Bad
```

## Authentication and Security

### Password Hashing

```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Usage in auth service
class AuthService:
    def register_user(self, email: str, password: str, name: str) -> User:
        """Register new user with hashed password."""
        password_hash = hash_password(password)
        return self.user_repo.create(
            email=email,
            name=name,
            password_hash=password_hash
        )

    def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user with password verification."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
```

### Session Management

```python
# app/core/security.py
import secrets
from datetime import datetime, timedelta

def create_session_token() -> str:
    """Generate secure random session token."""
    return secrets.token_urlsafe(32)

def create_session(user_id: int, expires_minutes: int = 1440) -> dict:
    """Create session data."""
    return {
        "token": create_session_token(),
        "user_id": user_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=expires_minutes)
    }

# Dependency for authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    token = credentials.credentials

    # Validate token and get user
    session = db.query(Session).filter(Session.token == token).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    if session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

## Testing Practices

### Unit Tests

```python
# tests/unit/test_validators.py
import pytest
from app.schemas.todo import TodoCreate
from pydantic import ValidationError

def test_todo_title_cannot_be_empty():
    """Test that empty title raises validation error."""
    with pytest.raises(ValidationError):
        TodoCreate(title="", description="Test")

def test_expires_date_must_be_after_starts_date():
    """Test date validation."""
    from datetime import datetime, timedelta

    starts = datetime.utcnow()
    expires = starts - timedelta(days=1)

    with pytest.raises(ValidationError):
        TodoCreate(
            title="Test",
            starts_date=starts,
            expires_date=expires
        )
```

### Integration Tests

```python
# tests/integration/test_todo_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_todo_success(authenticated_client):
    """Test successful TODO creation."""
    response = authenticated_client.post("/api/todos", json={
        "title": "Test TODO",
        "description": "Integration test",
        "status": "pending"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test TODO"
    assert "id" in data

def test_create_todo_requires_auth():
    """Test that TODO creation requires authentication."""
    response = client.post("/api/todos", json={
        "title": "Test TODO"
    })
    assert response.status_code == 401
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def authenticated_client(client, test_db):
    """Test client with authentication."""
    # Create test user
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    })

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

## Code Quality Tools

### Ruff (Linter and Formatter)

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### MyPy (Type Checker)

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin

[pydantic-mypy]
init_forbid_extra = True
init_typed = True
warn_required_dynamic_aliases = True
```

```bash
# Run type checking
mypy app/
```

## Logging

```python
# app/core/logging.py
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usage in code
from app.core.logging import logger

@router.post("/todos")
async def create_todo(todo_data: TodoCreate):
    logger.info(f"Creating TODO: {todo_data.title}")
    try:
        result = await todo_service.create_todo(todo_data)
        logger.info(f"TODO created successfully: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create TODO: {str(e)}", exc_info=True)
        raise
```

## Documentation

### Docstrings

```python
def get_user_todos(
    user_id: int,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[Todo]:
    """
    Retrieve TODOs for a user with optional filtering.

    Args:
        user_id: The ID of the user
        status: Optional status filter (pending, in_progress, completed)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return

    Returns:
        List of Todo objects matching the criteria

    Raises:
        ValueError: If user_id is invalid
        HTTPException: If user not found
    """
    pass
```

### API Documentation

FastAPI automatically generates OpenAPI docs. Enhance with descriptions:

```python
@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new TODO",
    description="Create a new TODO item for the authenticated user with optional tags and dates",
    responses={
        201: {"description": "TODO created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"}
    }
)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new TODO with the following information:
    - **title**: Required, max 200 characters
    - **description**: Optional, max 2000 characters
    - **status**: pending, in_progress, or completed
    - **starts_date**: Optional start date
    - **expires_date**: Optional deadline
    - **tag_ids**: Optional list of tag IDs
    """
    pass
```
