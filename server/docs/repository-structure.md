# Repository Structure

## Directory and File Structure

```
todoapp-server/
├── alembic/                    # Alembic database migrations
│   ├── versions/               # Migration version files
│   │   └── xxxx_initial.py     # Individual migration scripts
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration template
├── app/                        # Application source code
│   ├── api/                    # FastAPI routes and endpoints
│   │   ├── __init__.py
│   │   ├── auth.py             # /api/auth/* endpoints
│   │   ├── todos.py            # /api/todos/* endpoints
│   │   ├── tags.py             # /api/tags/* endpoints (optional)
│   │   └── deps.py             # Shared dependencies
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and environment variables
│   │   ├── security.py         # Password hashing, token generation
│   │   └── exceptions.py       # Custom exception classes
│   ├── db/                     # Database configuration
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy engine, session setup
│   │   └── base.py             # Base model import for Alembic
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── todo.py             # Todo model
│   │   ├── tag.py              # Tag model
│   │   └── todo_tag.py         # TodoTag association model
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── todo_repository.py
│   │   └── tag_repository.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py             # User request/response schemas
│   │   ├── todo.py             # Todo schemas
│   │   ├── tag.py              # Tag schemas
│   │   └── auth.py             # Authentication schemas
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── todo_service.py
│   │   └── tag_service.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── datetime_utils.py
│   │   └── validators.py
│   ├── __init__.py
│   └── main.py                 # FastAPI application entry point
├── tests/                      # Test files
│   ├── unit/                   # Unit tests
│   │   ├── test_services.py
│   │   ├── test_repositories.py
│   │   └── test_utils.py
│   ├── integration/            # Integration tests
│   │   ├── test_auth_api.py
│   │   ├── test_todo_api.py
│   │   └── test_tag_api.py
│   ├── conftest.py             # Pytest fixtures and configuration
│   └── __init__.py
├── docker-compose.yml          # Docker services for development
├── Dockerfile                  # Docker image definition (optional)
├── .env.example                # Example environment variables
├── .env                        # Actual environment variables (gitignored)
├── .gitignore                  # Git ignore patterns
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Poetry/project configuration
├── poetry.lock                 # Dependency lock file
├── requirements.txt            # Pip requirements (if not using Poetry)
├── README.md                   # Project overview
├── ruff.toml                   # Ruff configuration (optional, can be in pyproject.toml)
└── mypy.ini                    # MyPy type checking configuration
```

## Directory Roles

### `app/`

**Purpose**: Main application source code

**Responsibilities**:

- Contains all application logic
- Houses API routes, services, repositories, models
- Organized by Clean Architecture layers

**Guidelines**:

- All application code goes here
- Use absolute imports from `app.*`
- Keep organized by responsibility

### `app/api/`

**Purpose**: FastAPI routers and HTTP endpoints

**Responsibilities**:

- Define API routes and HTTP methods
- Handle request/response serialization
- Delegate business logic to services
- Apply authentication/authorization

**Guidelines**:

- One file per major resource (auth, todos, tags)
- Use APIRouter for modular routing
- Keep endpoints thin - delegate to services
- Use Pydantic schemas for validation
- Apply dependencies for auth, db sessions

**Example Structure**:

```python
# app/api/todos.py
from fastapi import APIRouter, Depends, status
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService
from app.api.deps import get_current_user, get_todo_service

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.get_user_todos(current_user.id)

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.create_todo(current_user.id, todo_data)
```

### `app/services/`

**Purpose**: Business logic layer

**Responsibilities**:

- Implement business rules
- Orchestrate between multiple repositories
- Data transformation and validation
- Transaction management

**Guidelines**:

- One service per major entity (AuthService, TodoService, TagService)
- Services should not directly access databases (use repositories)
- Keep services focused on business logic
- Services can call other services if needed
- Return domain models or DTOs, not ORM models directly

**Example**:

```python
# app/services/todo_service.py
from app.repositories.todo_repository import TodoRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.todo import TodoCreate, TodoUpdate
from app.models.todo import Todo

class TodoService:
    def __init__(self, todo_repo: TodoRepository, tag_repo: TagRepository):
        self.todo_repo = todo_repo
        self.tag_repo = tag_repo

    async def create_todo(self, user_id: int, data: TodoCreate) -> Todo:
        """Business logic for creating a TODO"""
        # Validate tags exist
        if data.tag_ids:
            tags = await self.tag_repo.get_by_ids(data.tag_ids)
            if len(tags) != len(data.tag_ids):
                raise ValueError("One or more tags not found")

        # Create TODO
        todo = await self.todo_repo.create(
            user_id=user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            starts_date=data.starts_date,
            expires_date=data.expires_date
        )

        # Associate tags
        if data.tag_ids:
            await self.todo_repo.add_tags(todo.id, data.tag_ids)

        return todo
```

### `app/repositories/`

**Purpose**: Data access layer

**Responsibilities**:

- Encapsulate database access
- Provide CRUD operations
- Build database queries
- Abstract SQLAlchemy details

**Guidelines**:

- One repository per model (UserRepository, TodoRepository, TagRepository)
- Methods return ORM models or primitives
- No business logic in repositories
- Use type hints for clarity
- Handle database sessions properly

**Example**:

```python
# app/repositories/todo_repository.py
from sqlalchemy.orm import Session, joinedload
from app.models.todo import Todo
from typing import Optional

class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.db.query(Todo)\
            .options(joinedload(Todo.tags))\
            .filter(Todo.id == todo_id)\
            .first()

    def get_all_for_user(self, user_id: int) -> list[Todo]:
        return self.db.query(Todo)\
            .filter(Todo.user_id == user_id)\
            .options(joinedload(Todo.tags))\
            .all()

    def create(self, **kwargs) -> Todo:
        todo = Todo(**kwargs)
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo: Todo, **kwargs) -> Todo:
        for key, value in kwargs.items():
            setattr(todo, key, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        self.db.delete(todo)
        self.db.commit()
```

### `app/models/`

**Purpose**: SQLAlchemy ORM models

**Responsibilities**:

- Define database schema
- Establish relationships between tables
- Set constraints and indexes

**Guidelines**:

- One model per file
- Use descriptive table names (plural: users, todos, tags)
- Define relationships explicitly
- Add indexes for frequently queried columns
- Include timestamps (created_at, updated_at)

**Example**:

```python
# app/models/todo.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum

class TodoStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TodoStatus), default=TodoStatus.PENDING, nullable=False)
    starts_date = Column(DateTime, nullable=True)
    expires_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="todos")
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")
```

### `app/schemas/`

**Purpose**: Pydantic schemas for validation and serialization

**Responsibilities**:

- Request body validation
- Response serialization
- Data transfer objects (DTOs)
- Type safety at API boundaries

**Guidelines**:

- Separate schemas for create, update, and response
- Use Pydantic Field for constraints
- Use validators for complex validation
- Set `from_attributes = True` for ORM model conversion

**Example**:

```python
# app/schemas/todo.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: TodoStatus = TodoStatus.PENDING
    starts_date: datetime | None = None
    expires_date: datetime | None = None

class TodoCreate(TodoBase):
    tag_ids: list[int] = []

    @field_validator('expires_date')
    @classmethod
    def validate_expires_date(cls, v, info):
        if v and info.data.get('starts_date') and v < info.data['starts_date']:
            raise ValueError('expires_date must be after starts_date')
        return v

class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TodoStatus | None = None
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] | None = None

class TodoResponse(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: list['TagResponse'] = []

    class Config:
        from_attributes = True
```

### `app/core/`

**Purpose**: Core configuration and utilities

**Responsibilities**:

- Application settings
- Security utilities (password hashing, tokens)
- Custom exceptions

**Guidelines**:

- Settings loaded from environment variables
- Use Pydantic BaseSettings for type-safe config
- Security functions isolated in security.py

**Example**:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "TODO App Demo Server"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    SESSION_EXPIRE_MINUTES: int = 1440
    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### `app/utils/`

**Purpose**: Utility functions

**Responsibilities**:

- Pure helper functions
- Date/time utilities
- Validators
- Formatters

**Guidelines**:

- Keep functions pure (no side effects)
- One utility module per category
- Export individual functions

**Example**:

```python
# app/utils/datetime_utils.py
from datetime import datetime, timedelta

def is_expired(expires_date: datetime) -> bool:
    """Check if a date has passed"""
    return datetime.utcnow() > expires_date

def days_until(target_date: datetime) -> int:
    """Calculate days until target date"""
    delta = target_date - datetime.utcnow()
    return max(0, delta.days)
```

### `alembic/`

**Purpose**: Database migration management

**Responsibilities**:

- Track database schema changes
- Generate migration scripts
- Apply/rollback migrations

**Guidelines**:

- Never edit migration files manually after creation
- Always test migrations on development database first
- Use descriptive migration messages

**Common Commands**:

```bash
# Create new migration
alembic revision --autogenerate -m "Add todos table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### `tests/`

**Purpose**: All test files

**Subdirectories**:

#### `tests/unit/`

**Purpose**: Unit tests for isolated components

**Guidelines**:

- Test services, repositories, utilities in isolation
- Use mocks for dependencies
- Fast execution

**Example**:

```python
# tests/unit/test_utils.py
from app.utils.datetime_utils import is_expired
from datetime import datetime, timedelta

def test_is_expired_returns_true_for_past_date():
    past_date = datetime.utcnow() - timedelta(days=1)
    assert is_expired(past_date) is True

def test_is_expired_returns_false_for_future_date():
    future_date = datetime.utcnow() + timedelta(days=1)
    assert is_expired(future_date) is False
```

#### `tests/integration/`

**Purpose**: Integration tests with real database

**Guidelines**:

- Use test database
- Test API endpoints end-to-end
- Verify database state changes

**Example**:

```python
# tests/integration/test_todo_api.py
from fastapi.testclient import TestClient

def test_create_todo(authenticated_client: TestClient, test_db):
    response = authenticated_client.post("/api/todos", json={
        "title": "Test TODO",
        "description": "Integration test",
        "status": "pending"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test TODO"
```

## File Naming Conventions

### Python Modules

- **Format**: snake_case (e.g., `todo_service.py`, `user_repository.py`)
- **Models**: Singular noun (e.g., `user.py`, `todo.py`, `tag.py`)
- **Services**: `{entity}_service.py` (e.g., `auth_service.py`)
- **Repositories**: `{entity}_repository.py` (e.g., `todo_repository.py`)
- **API Routes**: Resource name (e.g., `todos.py`, `auth.py`)

### Classes

- **Format**: PascalCase (e.g., `TodoService`, `UserRepository`, `TodoCreate`)
- **Models**: Entity name (e.g., `User`, `Todo`, `Tag`)
- **Services**: `{Entity}Service` (e.g., `TodoService`, `AuthService`)
- **Repositories**: `{Entity}Repository` (e.g., `TodoRepository`)
- **Schemas**: `{Entity}{Purpose}` (e.g., `TodoCreate`, `TodoResponse`, `UserUpdate`)

### Functions

- **Format**: snake_case (e.g., `get_todos`, `create_user`, `hash_password`)
- **Predicates**: Start with `is_` or `has_` (e.g., `is_expired`, `has_permission`)
- **Converters**: Use descriptive names (e.g., `to_dict`, `from_orm`)

### Variables

- **Format**: snake_case (e.g., `user_id`, `todo_list`, `session_token`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_TODO_LENGTH`, `SESSION_EXPIRE_MINUTES`)
- **Private**: Prefix with underscore (e.g., `_internal_helper`)

## Import Path Examples

### Using Absolute Imports

```python
# Good - absolute imports
from app.models.todo import Todo
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate, TodoResponse
from app.core.config import settings

# Avoid - relative imports
from ..models.todo import Todo
from ...services.todo_service import TodoService
```

### Import Order Convention

```python
# 1. Standard library imports
import os
from datetime import datetime
from typing import Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local application imports
from app.models.todo import Todo
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate, TodoResponse
from app.api.deps import get_current_user, get_todo_service
from app.core.config import settings
```

## Configuration Files Location

### Root Level Configuration

- `pyproject.toml`: Poetry/project configuration, tool settings (ruff, pytest, mypy)
- `alembic.ini`: Alembic migration configuration
- `docker-compose.yml`: Docker services for local development
- `.env`: Environment variables (gitignored)
- `.env.example`: Example environment variables (committed)
- `.gitignore`: Git ignore patterns
- `README.md`: Project documentation
- `requirements.txt`: Pip dependencies (if not using Poetry)
- `mypy.ini`: MyPy type checking configuration

### Hidden Directories

- `.venv/`: Python virtual environment (gitignored)
- `.pytest_cache/`: Pytest cache (gitignored)
- `.ruff_cache/`: Ruff cache (gitignored)
- `.mypy_cache/`: MyPy cache (gitignored)
- `__pycache__/`: Python bytecode cache (gitignored)

## File Size Guidelines

### Maximum File Sizes

- **API Routes**: < 300 lines per file
- **Services**: < 400 lines per file
- **Repositories**: < 300 lines per file
- **Models**: < 200 lines per file
- **Schemas**: < 250 lines per file

### When to Split Files

1. **Service**: > 400 lines → Split by feature or extract helper methods
2. **Repository**: > 300 lines → Split into specialized repositories
3. **API Routes**: > 300 lines → Split into multiple routers
4. **Schemas**: > 250 lines → Split by entity or operation type

## Best Practices

### File Organization

1. **Group by feature**: Keep related files together
2. **Shallow hierarchy**: Avoid deep nesting (max 3 levels)
3. **Colocate tests**: Mirror source structure in tests/
4. **Single responsibility**: One class/major function per file

### Code Organization Within Files

```python
# 1. Module docstring (if needed)
"""
Todo repository for database operations.
"""

# 2. Imports (standard, third-party, local)
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.todo import Todo

# 3. Constants
MAX_RESULTS = 100

# 4. Type definitions (if not in schemas)
# ...

# 5. Main class or functions
class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

# 6. Helper functions (if small and private)
def _build_filter_query(query, filters):
    # ...
    pass
```

### Package Initialization

Use `__init__.py` files to control what's exported:

```python
# app/services/__init__.py
from app.services.todo_service import TodoService
from app.services.auth_service import AuthService
from app.services.tag_service import TagService

__all__ = ["TodoService", "AuthService", "TagService"]
```

## Version Control Practices

### Files to Commit

- All source code in `app/`
- Test files in `tests/`
- Configuration files (`pyproject.toml`, `alembic.ini`, `docker-compose.yml`)
- Documentation (`README.md`, `docs/`)
- `.env.example` (but not `.env`)
- `requirements.txt` or `poetry.lock`

### Files to Ignore (in .gitignore)

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
.venv/
venv/
ENV/
env/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# Linting/Type checking
.ruff_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db
```

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:

```
feat(todos): add tag filtering to TODO list endpoint

- Add query parameter for tag filtering
- Update TodoRepository with filter logic
- Add integration tests for tag filtering

Closes #42
```

## Application Entry Point

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, todos, tags
from app.core.config import settings
from app.db.database import engine
from app.models import user, todo, tag  # Import for metadata

# Create database tables (for development only)
# In production, use Alembic migrations
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(tags.router)

@app.get("/")
async def root():
    return {"message": "TODO App Demo Server API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Running the Application

```bash
# Development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
