# Architecture

## Overview

TODO app demo server is built using FastAPI, a modern Python web framework. The application follows a Clean Architecture pattern that leverages FastAPI's dependency injection, Pydantic validation, and SQLAlchemy ORM for type-safe database operations.

## Technology Stack

### Backend Framework

- **FastAPI 0.100+**: Modern, fast web framework for building APIs
  - Chosen for automatic API documentation (Swagger/OpenAPI)
  - Built-in data validation with Pydantic
  - Async/await support for high performance
  - Excellent developer experience with type hints
- **Python 3.11+**: Programming language
  - Type hints for better IDE support and code quality
  - Modern async/await syntax
  - Rich ecosystem of libraries
- **Uvicorn**: ASGI server for running FastAPI applications
  - High-performance async server
  - Hot reload in development mode

### Database & ORM

- **PostgreSQL 15+**: Relational database
  - ACID compliance for data integrity
  - Robust support for complex queries
  - JSON field support if needed
  - Widely used in production environments
- **SQLAlchemy 2.0+**: SQL toolkit and ORM
  - Type-safe database operations
  - Migration support via Alembic
  - Relationship management
  - Connection pooling

### Authentication & Security

- **Session-based authentication**: Using database or cache-backed sessions
  - Session tokens stored securely
  - Token included in Authorization header
- **Passlib with bcrypt**: Password hashing
  - Industry-standard bcrypt algorithm
  - Configurable rounds (minimum 10)
  - Secure password verification

### Validation

- **Pydantic 2.0+**: Data validation using Python type annotations
  - Request body validation
  - Response serialization
  - Settings management
  - Type-safe schemas

### Local Development Environment

- **PostgreSQL in Docker**: Local database
- **Docker Compose**: Multi-container orchestration
- **Python virtual environment**: Dependency isolation

### Testing

- **Pytest**: Testing framework
  - Fixtures for test data
  - Parametrized tests
  - Coverage reporting
- **Pytest-asyncio**: Async test support for FastAPI
- **SQLAlchemy test fixtures**: In-memory or test database

### Code Quality

- **Ruff**: Fast Python linter and formatter
  - Replaces Flake8, Black, isort
  - Extremely fast (written in Rust)
  - Comprehensive rule set
- **MyPy**: Static type checker
  - Catches type errors before runtime
  - Ensures type hint consistency
- **Pre-commit hooks**: Automated code quality checks

### Development Tools

- **Poetry** or **pip-tools**: Dependency management
  - Lock file for reproducible builds
  - Development vs production dependencies
- **Alembic**: Database migration tool
  - Version controlled schema changes
  - Auto-generation from SQLAlchemy models
- **Python logging**: Built-in logging module
  - Structured logging
  - Different log levels (DEBUG, INFO, WARNING, ERROR)

## Dependencies

### Production Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"        # Web framework
uvicorn = "^0.24.0"         # ASGI server
sqlalchemy = "^2.0.0"       # ORM
alembic = "^1.12.0"         # Database migrations
psycopg2-binary = "^2.9.0"  # PostgreSQL driver
pydantic = "^2.5.0"         # Data validation
pydantic-settings = "^2.1.0" # Settings management
passlib = "^1.7.4"          # Password hashing
bcrypt = "^4.1.0"           # Bcrypt backend for passlib
python-multipart = "^0.0.6" # Form data parsing
```

### Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"           # Testing framework
pytest-asyncio = "^0.21.0"  # Async test support
pytest-cov = "^4.1.0"       # Coverage reporting
ruff = "^0.1.0"             # Linter and formatter
mypy = "^1.7.0"             # Type checker
pre-commit = "^3.5.0"       # Git hooks
httpx = "^0.25.0"           # HTTP client for testing FastAPI
```

## Development Tools and Practices

### Development Server

- **Command**: `uvicorn app.main:app --reload`
- **Port**: 8000 (configurable via environment variables)
- **Features**:
  - Hot reload on code changes
  - Automatic API documentation at `/docs` (Swagger UI)
  - Alternative docs at `/redoc` (ReDoc)
  - Interactive API testing

### Build Process

Since Python is interpreted, there's no traditional build step. However:

- **Dependency installation**: `poetry install` or `pip install -r requirements.txt`
- **Database migrations**: `alembic upgrade head`
- **Code quality checks**: `ruff check . && mypy .`

### Type Checking

- **Command**: `mypy app/`
- **Process**:
  1. Check type hints throughout codebase
  2. Verify Pydantic schema types
  3. Validate SQLAlchemy model types
  4. Report any type inconsistencies

### Testing

- **Framework**: Pytest
- **Commands**:
  - `pytest` or `pytest -v`: Run all tests
  - `pytest --cov=app`: Run with coverage report
  - `pytest -k test_name`: Run specific test
  - `pytest --lf`: Run last failed tests
- **Test Location**: Tests colocated in `tests/` directory

### Code Formatting and Linting

- **Tool**: Ruff (replaces Black, Flake8, isort)
- **Configuration**:
  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py311"

  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "W", "UP"]
  ignore = []
  ```
- **Commands**:
  - `ruff format .`: Format code
  - `ruff check .`: Lint code
  - `ruff check --fix .`: Auto-fix issues
- **Integration**: Pre-commit hook runs automatically

### Version Control

- **System**: Git
- **Branch Strategy**: Feature branches with main
- **Commit Convention**: Conventional Commits
  - `feat:` New features
  - `fix:` Bug fixes
  - `docs:` Documentation changes
  - `refactor:` Code refactoring
  - `test:` Adding or updating tests
  - `chore:` Maintenance tasks

## Architectural Patterns

### Clean Architecture Layers

The application follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│         API Layer (app/api/)                    │
│  - FastAPI routers and endpoints               │
│  - Request/response handling                    │
│  - Dependency injection setup                   │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│       Service Layer (app/services/)             │
│  - Business logic                               │
│  - Orchestration between repositories           │
│  - Data transformation                          │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│     Repository Layer (app/repositories/)        │
│  - Database access abstraction                  │
│  - CRUD operations                              │
│  - Query building                               │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│       Models Layer (app/models/)                │
│  - SQLAlchemy ORM models                        │
│  - Database schema definitions                  │
└─────────────────────────────────────────────────┘
```

**Example Implementation:**

```python
# app/api/todos.py - API Layer
from fastapi import APIRouter, Depends
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate, TodoResponse

router = APIRouter()

@router.post("/todos", response_model=TodoResponse)
async def create_todo(
    todo_data: TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user)
):
    """API endpoint delegates to service layer"""
    return await todo_service.create_todo(current_user.id, todo_data)


# app/services/todo_service.py - Service Layer
class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def create_todo(self, user_id: int, data: TodoCreate) -> Todo:
        """Business logic: validation, orchestration"""
        # Could add business rules here
        return await self.todo_repo.create(user_id=user_id, **data.dict())


# app/repositories/todo_repository.py - Repository Layer
class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, **kwargs) -> Todo:
        """Database access abstraction"""
        todo = Todo(**kwargs)
        self.db.add(todo)
        await self.db.commit()
        await self.db.refresh(todo)
        return todo
```

**Benefits:**

- Clear separation of concerns
- Testable components in isolation
- Easy to swap implementations
- Domain logic independent of framework

### Dependency Injection with FastAPI

FastAPI's `Depends()` provides clean dependency injection:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Service dependency
def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    todo_repo = TodoRepository(db)
    return TodoService(todo_repo)

# Authentication dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Validate token and return user
    return user

# Usage in endpoint
@router.get("/todos")
async def get_todos(
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.get_user_todos(current_user.id)
```

### Database Architecture

TODO app demo server uses **PostgreSQL** in production (and for local development). Development uses PostgreSQL in Docker for parity with production.

**Docker Compose Configuration (Development):**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: todoapp
      POSTGRES_PASSWORD: todoapp_dev_password
      POSTGRES_DB: todoapp_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todoapp"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**SQLAlchemy Integration:**

Configuration for database connection:

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,         # Connection pool size
    max_overflow=10      # Max connections beyond pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

**Schema Definition:**

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
```

**Database Client Usage:**

```python
# app/repositories/user_repository.py
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, name: str, password_hash: str) -> User:
        user = User(email=email, name=name, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
```

**Migrations:**

```bash
# Create new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations (production)
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

**Benefits:**

- **Type Safety**: SQLAlchemy 2.0 with type hints
- **Migration Management**: Alembic tracks schema changes
- **Connection Pooling**: Efficient database connections
- **Relationship Loading**: Eager/lazy loading support
- **Query Building**: Pythonic query interface
- **Transaction Support**: ACID guarantees

### State Management

**Server State:**

- All state stored in PostgreSQL database
- Session state in database or cache (if using Redis)
- No in-memory state (stateless API for scalability)

**Request Context:**

- Request-scoped database sessions via dependency injection
- Authentication context passed via `get_current_user` dependency
- No global state

### Error Handling

**FastAPI Exception Handling:**

```python
from fastapi import HTTPException, status

# Custom exceptions
class TodoNotFoundError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

# Exception handlers
@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "TODO not found"}
    )

# Usage in service
class TodoService:
    async def get_todo(self, todo_id: int, user_id: int) -> Todo:
        todo = await self.todo_repo.get_by_id(todo_id)
        if not todo:
            raise TodoNotFoundError()
        if todo.user_id != user_id:
            raise UnauthorizedError()
        return todo
```

**Validation Errors:**

FastAPI automatically handles Pydantic validation errors and returns 422 responses with detailed error messages.

### Form Handling and Validation

**Pydantic Schemas for Validation:**

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
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: TodoStatus = TodoStatus.PENDING
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] = []

    @field_validator('expires_date')
    @classmethod
    def validate_expires_date(cls, v, info):
        if v and info.data.get('starts_date') and v < info.data['starts_date']:
            raise ValueError('expires_date must be after starts_date')
        return v

class TodoResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: TodoStatus
    starts_date: datetime | None
    expires_date: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list['TagResponse'] = []

    class Config:
        from_attributes = True  # Formerly orm_mode in Pydantic v1
```

## Performance Requirements

### API Response Times

| Endpoint Type        | Target  | 95th Percentile |
| -------------------- | ------- | --------------- |
| GET (single record)  | < 100ms | < 200ms         |
| GET (list with filter) | < 300ms | < 500ms         |
| POST/PUT/DELETE      | < 200ms | < 400ms         |
| Authentication       | < 150ms | < 300ms         |

### Optimization Strategies

#### Server-Side Optimization

1. **PostgreSQL**:
   - Indexes on frequently queried columns (email, user_id, status)
   - Connection pooling (5-10 connections)
   - Query optimization with EXPLAIN ANALYZE
   - Eager loading for relationships to avoid N+1 queries

2. **SQLAlchemy**:
   - Use `joinedload()` or `selectinload()` for relationships
   - Batch operations where possible
   - Efficient pagination with `limit()` and `offset()`
   - Query result caching for expensive queries

3. **FastAPI**:
   - Async endpoints for I/O-bound operations
   - Dependency caching where appropriate
   - Response model optimization (exclude unnecessary fields)

#### Database Scaling

- Read replicas for read-heavy workloads (future consideration)
- Proper indexing on foreign keys and search fields
- Partitioning for large tables (if TODO count grows significantly)
- Connection pooling tuned for concurrent users

### Monitoring and Observability

#### Metrics Collection

- **Application Metrics**: Request count, response times, error rates
- **Database Metrics**: Query times, connection pool usage, slow queries
- **System Metrics**: CPU, memory, disk usage

#### Tools

- **Python logging**: Structured logging with JSON format
- **Uvicorn access logs**: HTTP request logging
- **PostgreSQL logs**: Query logging for slow queries

## Security Architecture

### Authentication

- Session-based authentication with secure tokens
- Tokens stored in database with expiration
- CSRF protection (if using cookies)
- Password requirements enforced via Pydantic validation

### Authorization

- User ID extracted from validated session
- All TODO operations check `todo.user_id == current_user.id`
- Database-level foreign key constraints

### Data Protection

- HTTPS in production (TLS 1.2+)
- Password hashing with bcrypt (12 rounds minimum)
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)
- XSS protection through proper JSON serialization

### Secure Headers

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Deployment Architecture

### Environment Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TODO App Demo Server"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    SESSION_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    BCRYPT_ROUNDS: int = 12

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Example .env file (Development):**

```bash
# Application
APP_NAME="TODO App Demo Server"
DEBUG=true

# Database
DATABASE_URL=postgresql://todoapp:todoapp_dev_password@localhost:5432/todoapp_dev

# Security
SECRET_KEY=your-secret-key-here-change-in-production
SESSION_EXPIRE_MINUTES=1440
BCRYPT_ROUNDS=12

# Server
HOST=0.0.0.0
PORT=8000
```

**Example .env file (Production):**

```bash
# Application
APP_NAME="TODO App Demo Server"
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/todoapp_prod

# Security
SECRET_KEY=strong-random-secret-key
SESSION_EXPIRE_MINUTES=1440
BCRYPT_ROUNDS=12

# Server
HOST=0.0.0.0
PORT=8000
```

### Production Server

**Deployment Platform**: Local machine / VPS / Cloud VM

- **ASGI Server**: Uvicorn with multiple workers
- **Process Manager**: Systemd or Supervisor
- **Reverse Proxy**: Nginx (for HTTPS termination, static files)
- **Database**: PostgreSQL (separate instance)
- **Monitoring**: Basic logging

**Example Uvicorn Production Command:**

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-access-log \
  --log-level info
```

## Testing Strategy

### Unit Tests

Test individual functions and methods in isolation:

```python
# tests/unit/test_services.py
import pytest
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate

def test_todo_service_validates_dates():
    """Unit test with mocked repository"""
    mock_repo = MockTodoRepository()
    service = TodoService(mock_repo)

    # Test that service enforces business rules
    with pytest.raises(ValueError):
        todo_data = TodoCreate(
            title="Test",
            starts_date=datetime(2024, 2, 10),
            expires_date=datetime(2024, 2, 5)  # Before starts_date
        )
```

### Integration Tests

Test with real database:

```python
# tests/integration/test_todo_api.py
from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures import test_db, authenticated_client

def test_create_todo_integration(authenticated_client, test_db):
    """Integration test with real database"""
    response = authenticated_client.post("/api/todos", json={
        "title": "Test TODO",
        "description": "Integration test",
        "status": "pending"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test TODO"

    # Verify in database
    todo = test_db.query(Todo).filter(Todo.id == data["id"]).first()
    assert todo is not None
```

### Test Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All API endpoints
- **Critical Paths**: 100% coverage (authentication, authorization, data integrity)

## Configuration Files

### pyproject.toml (Poetry)

```toml
[tool.poetry]
name = "todoapp-server"
version = "0.1.0"
description = "TODO app demo server with FastAPI"
authors = ["Your Name <email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
psycopg2-binary = "^2.9.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
passlib = "^1.7.4"
bcrypt = "^4.1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
mypy = "^1.7.0"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Future Architectural Considerations

### Potential Enhancements

1. **Caching Layer**: Add Redis for session storage and query caching
2. **Background Tasks**: Celery for async task processing (email notifications, cleanup jobs)
3. **API Versioning**: Add `/api/v1/` prefix for future API evolution
4. **GraphQL**: Consider GraphQL API alongside REST
5. **WebSockets**: Real-time TODO updates across clients
6. **Full-text Search**: PostgreSQL full-text search or Elasticsearch integration
7. **File Attachments**: Add file upload support for TODO attachments

### Scalability Path

1. **Phase 1** (Current): Single server with PostgreSQL
2. **Phase 2**: Add Redis for sessions and caching, multiple Uvicorn workers
3. **Phase 3**: Horizontal scaling with load balancer, read replicas for PostgreSQL
4. **Phase 4**: Microservices architecture if complexity grows
