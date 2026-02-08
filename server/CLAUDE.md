# TODO App Demo Server - Claude Context

This document provides a concise overview of the TODO App Demo Server project for AI assistants. For detailed information, refer to the comprehensive documentation in the `docs/` directory.

---

## Project Overview

**Type**: Backend REST API Server
**Purpose**: Task management system with user authentication and tag-based organization
**Status**: Documentation complete, implementation pending
**Architecture**: Clean Architecture with FastAPI

**Key Features**:
1. User authentication (session-based)
2. TODO CRUD operations with status tracking
3. Tag system with color coding
4. Tag-based filtering
5. User profile management

---

## Technology Stack

### Core Technologies
- **Framework**: FastAPI 0.104+ (Python 3.11+)
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.5+
- **Authentication**: Session-based with bcrypt
- **Migrations**: Alembic

### Development Tools
- **Testing**: Pytest with pytest-asyncio, pytest-cov
- **Linting/Formatting**: Ruff
- **Type Checking**: MyPy
- **Package Manager**: Poetry or pip

### Local Development
- **Docker Compose**: PostgreSQL service
- **Environment**: Python virtual environment (.venv)

---

## Domain Model (Ubiquitous Language)

> Full reference: `docs/ubiquitous-language.md`

### Core Entities

#### User
- Authenticated account holder
- Properties: id, email, name, password_hash, created_at, updated_at
- Owns multiple TODOs

#### TODO
- Task item belonging to a user
- Properties: id, user_id, title, description, status, starts_date, expires_date, created_at, updated_at
- Status: `pending` | `in_progress` | `completed`
- Can have multiple tags

#### Tag
- Label for categorizing TODOs
- Properties: id, name, color_code, created_at, updated_at
- Color code: hex format (e.g., #FF5733)
- Many-to-many relationship with TODOs

#### TodoTag (Association)
- Links TODOs to Tags
- Properties: id, todo_id, tag_id, created_at

### Terminology Rules
- ✅ Use: TODO (not Task), Tag (not Category), Sign In/Sign Out (not Login/Logout)
- ✅ API paths: `/api/todos`, `/api/tags`, `/api/auth/signin`
- ✅ Status values: `pending`, `in_progress`, `completed`

---

## Architecture

> Full reference: `docs/architecture.md`

### Clean Architecture Layers

```
API Layer (app/api/)
    ↓ delegates to
Service Layer (app/services/)
    ↓ uses
Repository Layer (app/repositories/)
    ↓ accesses
Models Layer (app/models/)
    ↓ persists to
Database (PostgreSQL)
```

### Layer Responsibilities

**API Layer** (`app/api/`):
- FastAPI routers and endpoints
- Request/response handling
- Authentication via dependencies
- Delegates to services

**Service Layer** (`app/services/`):
- Business logic
- Data validation
- Transaction orchestration
- Authorization checks

**Repository Layer** (`app/repositories/`):
- Database access abstraction
- CRUD operations
- Query building
- No business logic

**Models Layer** (`app/models/`):
- SQLAlchemy ORM models
- Database schema definitions
- Relationships

### Key Patterns

**Dependency Injection**:
```python
from fastapi import Depends

@router.post("/todos")
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.create_todo(current_user.id, todo_data)
```

**Repository Pattern**:
```python
class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()
```

---

## Directory Structure

> Full reference: `docs/repository-structure.md`

```
todoapp-server/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic config
├── app/                        # Application code
│   ├── api/                    # FastAPI endpoints
│   │   ├── auth.py             # /api/auth/* routes
│   │   ├── todos.py            # /api/todos/* routes
│   │   ├── tags.py             # /api/tags/* routes
│   │   └── deps.py             # Shared dependencies
│   ├── core/                   # Core config
│   │   ├── config.py           # Settings (env vars)
│   │   ├── security.py         # Password hashing, sessions
│   │   └── exceptions.py       # Custom exceptions
│   ├── db/                     # Database setup
│   │   └── database.py         # SQLAlchemy engine
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── todo.py
│   │   ├── tag.py
│   │   └── todo_tag.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── todo_repository.py
│   │   └── tag_repository.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── todo.py
│   │   └── tag.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── todo_service.py
│   │   └── tag_service.py
│   ├── utils/                  # Helper functions
│   └── main.py                 # FastAPI app entry point
├── tests/                      # Test files
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── docs/                       # Documentation
├── docker-compose.yml          # PostgreSQL service
├── .env.example                # Environment template
├── pyproject.toml              # Poetry config
├── requirements.txt            # Dependencies
└── alembic.ini                 # Alembic config
```

---

## API Endpoints

> Full reference: `docs/functional-design.md`

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login (returns session token)
- `POST /api/auth/signout` - User logout

### TODOs (All require authentication)
- `GET /api/todos` - List user's TODOs (supports filtering by status, tags, pagination)
- `GET /api/todos/:id` - Get single TODO
- `POST /api/todos` - Create new TODO
- `PUT /api/todos/:id` - Update TODO
- `DELETE /api/todos/:id` - Delete TODO

### Tags (Optional)
- `GET /api/tags` - List user's tags
- `POST /api/tags` - Create new tag

### Health Check
- `GET /health` - Health check endpoint

---

## Data Models

> Full reference: `docs/functional-design.md`

### User Model
```python
class User(Base):
    __tablename__ = "users"

    id: int                      # Primary key
    email: str                   # Unique, indexed
    name: str
    password_hash: str           # Bcrypt hashed
    created_at: datetime
    updated_at: datetime

    todos: relationship("Todo")  # One-to-many
```

### Todo Model
```python
class Todo(Base):
    __tablename__ = "todos"

    id: int
    user_id: int                 # FK to users, indexed
    title: str                   # Max 200 chars, required
    description: str | None      # Max 2000 chars
    status: TodoStatus           # Enum
    starts_date: datetime | None
    expires_date: datetime | None
    created_at: datetime
    updated_at: datetime

    user: relationship("User")
    tags: relationship("Tag", secondary="todo_tags")

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

### Tag Model
```python
class Tag(Base):
    __tablename__ = "tags"

    id: int
    name: str                    # Max 50 chars
    color_code: str              # Hex format (#RRGGBB)
    created_at: datetime
    updated_at: datetime

    todos: relationship("Todo", secondary="todo_tags")
```

### TodoTag (Association)
```python
class TodoTag(Base):
    __tablename__ = "todo_tags"

    id: int
    todo_id: int                 # FK to todos
    tag_id: int                  # FK to tags
    created_at: datetime

    # Unique constraint: (todo_id, tag_id)
```

---

## Pydantic Schemas

> Full reference: `docs/functional-design.md`, `docs/development-guidelines.md`

### TODO Schemas
```python
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: TodoStatus = TodoStatus.PENDING
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] = []

    @field_validator('expires_date')
    @classmethod
    def validate_dates(cls, v, info):
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
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True
```

---

## Development Workflow

> Full reference: `docs/environments.md`, `docs/development-guidelines.md`

### Setup (First Time)
```bash
# 1. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL
docker-compose up -d postgres

# 4. Configure environment
cp .env.example .env

# 5. Run migrations
alembic upgrade head

# 6. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Daily Development
```bash
# Start PostgreSQL (if not running)
docker-compose up -d postgres

# Activate virtual environment
source .venv/bin/activate

# Start dev server with hot reload
uvicorn app.main:app --reload
```

### Database Changes
```bash
# 1. Modify models in app/models/
# 2. Create migration
alembic revision --autogenerate -m "Description"
# 3. Review migration in alembic/versions/
# 4. Apply migration
alembic upgrade head
```

### Code Quality
```bash
# Format code
ruff format .

# Check linting
ruff check .

# Type checking
mypy app/

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

---

## Testing Strategy

> Full reference: `docs/test-concepts.md`

### Test Pyramid
- **60-75% Unit Tests**: Fast, isolated, mock dependencies
- **20-30% Integration Tests**: Real database, API endpoints
- **5-10% E2E Tests**: Full user journeys (requires frontend)

### Test Structure
```
tests/
├── conftest.py              # Fixtures: test_db, client, authenticated_client
├── unit/
│   ├── test_utils.py        # Pure functions
│   ├── test_validators.py   # Pydantic validators
│   └── test_services.py     # Service logic (mocked repos)
└── integration/
    ├── test_auth_api.py     # Auth endpoints
    ├── test_todo_api.py     # TODO endpoints
    └── test_tag_api.py      # Tag endpoints
```

### Key Fixtures (conftest.py)
```python
@pytest.fixture
def test_db():
    """Test database with clean state per test"""

@pytest.fixture
def client(test_db):
    """FastAPI TestClient with test database"""

@pytest.fixture
def authenticated_client(client, test_db):
    """TestClient with authenticated user and token"""
```

### Coverage Goals
- Overall: >80%
- Critical paths (auth, authorization): 100%
- API endpoints: 100%

---

## Naming Conventions

> Full reference: `docs/development-guidelines.md`, `docs/ubiquitous-language.md`

### Python Code
- **Files/Modules**: `snake_case` (todo_service.py)
- **Classes**: `PascalCase` (TodoService, UserRepository)
- **Functions/Methods**: `snake_case` (get_todos, create_user)
- **Variables**: `snake_case` (user_id, todo_list)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_TODO_LENGTH)
- **Boolean**: `is_/has_/can_` prefix (is_authenticated, has_permission)

### Database
- **Tables**: Plural snake_case (users, todos, tags, todo_tags)
- **Columns**: snake_case (user_id, created_at, color_code)

### API Endpoints
- **Paths**: Plural nouns (/api/todos, /api/tags)
- **Auth**: /api/auth/signin (not /api/auth/login)

### Pydantic Schemas
- **Create**: EntityCreate (TodoCreate, UserCreate)
- **Update**: EntityUpdate (TodoUpdate, UserUpdate)
- **Response**: EntityResponse (TodoResponse, UserResponse)

---

## Security

> Full reference: `docs/architecture.md`, `docs/development-guidelines.md`

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Authentication
- **Method**: Session-based (not JWT)
- **Storage**: Database or cache (Redis)
- **Token**: Secure random string (secrets.token_urlsafe(32))
- **Expiration**: Configurable (default: 1440 minutes = 24 hours)

### Authorization
- **Pattern**: Check `todo.user_id == current_user.id` for all operations
- **Dependency**: `get_current_user` validates session token
- **Errors**: 401 (unauthenticated), 403 (unauthorized)

### Input Validation
- **Tool**: Pydantic schemas with Field validators
- **Protection**: SQL injection (SQLAlchemy ORM), XSS (JSON serialization)

---

## Environment Variables

> Full reference: `docs/environments.md`

### Required Variables (.env)
```bash
# Application
APP_NAME="TODO App Demo Server"
DEBUG=true                    # false in production

# Database
DATABASE_URL=postgresql://todoapp:todoapp_dev_password@localhost:5432/todoapp_dev

# Security
SECRET_KEY=your-secret-key-here
SESSION_EXPIRE_MINUTES=1440
BCRYPT_ROUNDS=12

# Server
HOST=0.0.0.0
PORT=8000
```

### Configuration Loading (app/core/config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    SESSION_EXPIRE_MINUTES: int = 1440
    BCRYPT_ROUNDS: int = 12
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Code Quality Standards

> Full reference: `docs/development-guidelines.md`

### Ruff Configuration (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

### MyPy Configuration (mypy.ini)
```ini
[mypy]
python_version = 3.11
warn_return_any = True
disallow_untyped_defs = True
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin
```

### Type Hints (Required)
```python
# All functions must have type hints
def get_user_todos(
    user_id: int,
    status: str | None = None
) -> list[Todo]:
    pass
```

### Docstrings (Google Style)
```python
def create_todo(user_id: int, data: TodoCreate) -> Todo:
    """
    Create a new TODO for a user.

    Args:
        user_id: ID of the user creating the TODO
        data: TODO creation data

    Returns:
        Created TODO instance

    Raises:
        ValueError: If validation fails
    """
```

---

## Database Operations Best Practices

> Full reference: `docs/development-guidelines.md`

### Session Management
```python
# Use dependency injection for sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In endpoint
@router.post("/todos")
async def create_todo(db: Session = Depends(get_db)):
    pass
```

### Avoid N+1 Queries
```python
# Bad: N+1 queries
todos = db.query(Todo).all()
for todo in todos:
    tags = todo.tags  # Additional query per TODO

# Good: Eager loading
from sqlalchemy.orm import joinedload

todos = db.query(Todo)\
    .options(joinedload(Todo.tags))\
    .all()
```

### Efficient Queries
```python
# Bad: Load all then filter in Python
todos = db.query(Todo).all()
active = [t for t in todos if t.status != "completed"]

# Good: Filter in database
active = db.query(Todo)\
    .filter(Todo.status != "completed")\
    .all()
```

### Indexes
```python
# Add indexes to frequently queried columns
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String, index=True)
    created_at = Column(DateTime, index=True)
```

---

## Common Patterns

### API Endpoint Pattern
```python
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.todo import TodoCreate, TodoResponse
from app.services.todo_service import TodoService
from app.api.deps import get_current_user, get_todo_service

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """Create a new TODO for the authenticated user."""
    return await todo_service.create_todo(current_user.id, todo_data)
```

### Service Pattern
```python
class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def create_todo(self, user_id: int, data: TodoCreate) -> Todo:
        """Create TODO with business logic validation."""
        # Business rule: expires_date must be after starts_date
        if data.expires_date and data.starts_date:
            if data.expires_date < data.starts_date:
                raise ValueError("expires_date must be after starts_date")

        return self.todo_repo.create(user_id=user_id, **data.dict())

    async def get_todo(self, todo_id: int, user_id: int) -> Todo:
        """Get TODO with authorization check."""
        todo = self.todo_repo.get_by_id(todo_id)
        if not todo:
            raise TodoNotFoundError()
        if todo.user_id != user_id:
            raise UnauthorizedAccessError()
        return todo
```

### Repository Pattern
```python
class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

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
```

---

## Non-Functional Requirements

> Full reference: `docs/product-requirements.md`

### Performance
- API response time: <500ms for simple queries, <2s for complex (95th percentile)
- Support: 10 concurrent users (demo scope)

### Security
- Password hashing: bcrypt (12 rounds minimum)
- SQL injection: Prevented via SQLAlchemy ORM
- XSS: Prevented via Pydantic validation
- Sessions: Secure token storage

### Reliability
- Database transactions for complex operations
- Foreign key constraints at DB level
- ACID guarantees

### Maintainability
- Test coverage: >80% overall
- Critical paths: >90% coverage
- Clean Architecture pattern
- Type hints throughout

---

## Implementation Status

**Current State**: Documentation complete, no implementation code exists yet

**Next Steps**:
1. Create project structure (directories, __init__.py files)
2. Set up Docker Compose and .env
3. Implement database models and migrations
4. Build core utilities (security, config)
5. Implement repositories → services → API endpoints
6. Write tests alongside implementation
7. Achieve >80% test coverage

Detailed implementation roadmap available in: `docs/DOCUMENTATION_REVIEW_REPORT.md`

---

## Documentation References

For detailed information, refer to:

- **Product Requirements**: `docs/product-requirements.md` - Business needs, functional/non-functional requirements
- **Functional Design**: `docs/functional-design.md` - API specs, data models, flows
- **Architecture**: `docs/architecture.md` - Technology stack, patterns, configuration
- **Ubiquitous Language**: `docs/ubiquitous-language.md` - Domain terminology, naming rules
- **Test Concepts**: `docs/test-concepts.md` - Testing strategy, examples, fixtures
- **Repository Structure**: `docs/repository-structure.md` - Directory organization, file naming
- **Development Guidelines**: `docs/development-guidelines.md` - Coding standards, best practices
- **Environments**: `docs/environments.md` - Setup instructions, deployment
- **Review Report**: `docs/DOCUMENTATION_REVIEW_REPORT.md` - Comprehensive review and implementation roadmap

---

## API Endpoints Available

Once the server is running, the following endpoints are available:

- **Root**: http://localhost:8000/ - API information and welcome message
- **Health Check**: http://localhost:8000/health - Service health status
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc - Alternative API documentation

### Authentication Endpoints (To be implemented)
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login (returns session token)
- `POST /api/auth/signout` - User logout

### TODO Endpoints (To be implemented)
- `GET /api/todos` - List user's TODOs
- `GET /api/todos/:id` - Get single TODO
- `POST /api/todos` - Create new TODO
- `PUT /api/todos/:id` - Update TODO
- `DELETE /api/todos/:id` - Delete TODO

### Tag Endpoints (To be implemented)
- `GET /api/tags` - List user's tags
- `POST /api/tags` - Create new tag

---

## Quick Commands Reference

### Docker Compose (Recommended)

```bash
# Build and start all services
docker compose build
docker compose up -d

# View logs
docker compose logs -f app              # FastAPI logs
docker compose logs -f postgres         # PostgreSQL logs
docker compose logs -f                  # All logs

# Check status
docker compose ps

# Stop services
docker compose down                     # Stop and remove containers
docker compose down -v                  # Also remove volumes (database data)

# Restart services
docker compose restart app              # Restart FastAPI only
docker compose restart                  # Restart all services

# Execute commands in containers
docker compose exec app bash            # Shell access to app container
docker compose exec app pytest          # Run tests
docker compose exec app alembic upgrade head  # Run migrations
docker compose exec postgres psql -U todoapp todoapp_dev  # PostgreSQL shell
```

### Local Development (Without Docker)

```bash
# Setup
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d postgres           # Start PostgreSQL only
cp .env.example .env
alembic upgrade head

# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Start dev server
```

### Database Commands

```bash
# With Docker
docker compose exec app alembic revision --autogenerate -m "msg"  # Create migration
docker compose exec app alembic upgrade head                      # Apply migrations
docker compose exec app alembic downgrade -1                      # Rollback one migration

# Local (without Docker)
alembic revision --autogenerate -m "msg"    # Create migration
alembic upgrade head                        # Apply migrations
alembic downgrade -1                        # Rollback one migration
```

### Code Quality

```bash
# With Docker
docker compose exec app ruff format .       # Format code
docker compose exec app ruff check .        # Lint code
docker compose exec app mypy app/           # Type check

# Local (without Docker)
ruff format .                               # Format code
ruff check .                                # Lint code
mypy app/                                   # Type check
```

### Testing

```bash
# With Docker
docker compose exec app pytest                              # Run all tests
docker compose exec app pytest -v                           # Verbose output
docker compose exec app pytest --cov=app --cov-report=html  # Coverage report
docker compose exec app pytest -k test_name                 # Run specific test

# Local (without Docker)
pytest                                      # Run all tests
pytest -v                                   # Verbose output
pytest --cov=app --cov-report=html         # Coverage report
pytest -k test_name                        # Run specific test
```

---

**Last Updated**: 2026-02-08
