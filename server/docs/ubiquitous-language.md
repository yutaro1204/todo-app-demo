# Ubiquitous Language

## Purpose

This document defines the domain-specific terminology and concepts used throughout the TODO app demo server codebase. All team members, code, documentation, and conversations should use these terms consistently to maintain a shared understanding of the domain.

## Core Entities

### TODO App Demo Server

**Definition**: A FastAPI-based REST API server that provides backend functionality for a task management application.

**Context**: Used when referring to the overall system, backend infrastructure, and API services.

**Examples**:

- "The TODO app demo server handles all authentication and data persistence"
- "Deploy the TODO app demo server to the production environment"

**Code References**:

- Application entry point in `main.py` or `app.py`
- API routes defined in `app/api/` directory
- FastAPI application instance

### User

**Definition**: An authenticated account holder who can create and manage their own TODO items and tags.

**Aliases**: Account, Account Holder

**Context**: A user must register with email and password, then authenticate to access their TODOs. Each user's data is completely isolated from other users.

**Properties**:

- `id`: Unique identifier (integer, auto-increment)
- `email`: Unique email address for authentication
- `name`: Display name
- `password_hash`: Securely hashed password (bcrypt)
- `created_at`: Registration timestamp
- `updated_at`: Last profile update timestamp

**Examples**:

- "A user can create multiple TODOs"
- "Each user owns their TODO list"
- "Users authenticate with email and password"

**Code References**:

```python
class User(Base):
    __tablename__ = "users"

    id: int
    email: str  # unique, indexed
    name: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
```

### TODO

**Definition**: A task or action item that belongs to a user, containing a title, optional description, status, and optional date range.

**Aliases**: Task, Todo Item, Action Item

**Context**: TODOs are the primary domain entity. Each TODO is owned by exactly one user and can be tagged with multiple tags for organization.

**Properties**:

- `id`: Unique identifier
- `user_id`: Owner's user ID (foreign key)
- `title`: Short description of the task (required)
- `description`: Detailed notes (optional)
- `status`: Current state (pending, in_progress, completed)
- `starts_date`: When the task begins (optional)
- `expires_date`: Deadline for completion (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `tags`: Associated tags for categorization

**Examples**:

- "Create a new TODO with title 'Buy groceries'"
- "Update the TODO status to completed"
- "Filter TODOs by tag to see only work-related tasks"

**Code References**:

```python
class Todo(Base):
    __tablename__ = "todos"

    id: int
    user_id: int  # FK to users
    title: str
    description: str | None
    status: TodoStatus
    starts_date: datetime | None
    expires_date: datetime | None
    created_at: datetime
    updated_at: datetime

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

### Tag

**Definition**: A label or category that can be assigned to TODOs to organize and filter them, typically with an associated color for visual identification.

**Aliases**: Label, Category

**Context**: Tags provide a flexible categorization system. A TODO can have multiple tags, and a tag can be assigned to multiple TODOs (many-to-many relationship).

**Properties**:

- `id`: Unique identifier
- `name`: Tag label (e.g., "work", "personal", "urgent")
- `color_code`: Hex color code for visual display (e.g., "#FF5733")
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Examples**:

- "Assign the 'work' and 'urgent' tags to this TODO"
- "Filter the dashboard to show only TODOs with the 'personal' tag"
- "Create a new tag called 'shopping' with green color"

**Code References**:

```python
class Tag(Base):
    __tablename__ = "tags"

    id: int
    name: str
    color_code: str  # hex format like #FF5733
    created_at: datetime
    updated_at: datetime
```

## Core Concepts

### Session

**Definition**: An authenticated user's active connection to the system, tracked by a session token issued after successful sign-in.

**Properties**:

- Session token (string, unique)
- Associated user ID
- Expiration time
- Creation timestamp

**Examples**:

- "After signing in, the user receives a session token"
- "The session token must be included in the Authorization header"
- "Signing out invalidates the session"

**Code References**:

```python
# Session may be stored in database, cache, or JWT
class Session:
    token: str
    user_id: int
    expires_at: datetime
    created_at: datetime
```

### Dashboard

**Definition**: The primary user interface that displays a user's TODOs in a visual, filterable format.

**Context**: The dashboard is client-side (separate frontend project) but the term refers to the conceptual view of TODOs. The server provides the data through the GET /api/todos endpoint.

**Properties**:

- Displays all user's TODOs
- Allows filtering by tags
- Shows TODO status visually
- Displays date information (starts_date, expires_date)
- Shows color-coded tags

**Examples**:

- "The dashboard shows 10 pending TODOs"
- "Filter the dashboard to show only work-related TODOs"
- "The dashboard graphically displays existing TODOs with their tags"

### Todo-Tag Association

**Definition**: The many-to-many relationship between TODOs and tags, tracked through an association table.

**Context**: Allows flexible categorization where one TODO can have multiple tags and one tag can be applied to multiple TODOs.

**Properties**:

- `todo_id`: Reference to TODO
- `tag_id`: Reference to Tag
- `created_at`: When the tag was assigned to the TODO

**Examples**:

- "Assigning the 'urgent' tag creates a new todo-tag association"
- "Removing a tag deletes the todo-tag association"
- "Query all TODOs that have the 'work' tag through the association table"

**Code References**:

```python
class TodoTag(Base):
    __tablename__ = "todo_tags"

    id: int
    todo_id: int  # FK to todos
    tag_id: int  # FK to tags
    created_at: datetime

    # Unique constraint on (todo_id, tag_id)
```

## Business Concepts

### Authentication

**Definition**: The process of verifying a user's identity through email and password credentials.

**Context**: Required before accessing any TODO operations. Uses session-based authentication.

**Examples**:

- "User authentication requires valid email and password"
- "Authentication fails if the password is incorrect"
- "An authenticated user receives a session token"

### Authorization

**Definition**: Verifying that an authenticated user has permission to access or modify a specific resource.

**Context**: Users can only access their own TODOs. The server checks that TODO.user_id matches the authenticated user's ID.

**Examples**:

- "Users are authorized to view only their own TODOs"
- "Authorization check prevents user A from deleting user B's TODO"
- "The server returns 403 Forbidden if authorization fails"

### TODO Status

**Definition**: The current state of a TODO item, indicating its progress toward completion.

**Values**:

- **pending**: TODO is created but work hasn't started
- **in_progress**: Work on the TODO has begun
- **completed**: TODO is finished

**Examples**:

- "New TODOs default to 'pending' status"
- "Update the status to 'completed' when the task is done"
- "Filter to show only 'in_progress' TODOs"

**Code References**:

```python
from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

### Date Range

**Definition**: The optional time period for a TODO, specified by starts_date and expires_date.

**Context**: Helps users plan when to start tasks and track deadlines.

**Properties**:

- `starts_date`: Optional datetime when task should begin
- `expires_date`: Optional datetime deadline for completion

**Examples**:

- "Set the TODO to start on February 10 and expire on February 15"
- "TODOs with an expires_date in the past are overdue"
- "Filter to show TODOs expiring this week"

### Color Code

**Definition**: A hexadecimal color value (e.g., #FF5733) assigned to tags for visual identification.

**Context**: Used to color-code tags in the dashboard UI for quick recognition.

**Examples**:

- "The 'work' tag has color code #FF5733 (red-orange)"
- "Personal tags use #28B463 (green)"
- "Each tag has a unique color code for easy visual distinction"

## Technical Terms

### FastAPI Endpoint

**Definition**: A route handler function decorated with @app.get(), @app.post(), etc., that handles HTTP requests.

**Context**: Endpoints define the REST API interface. Each endpoint maps to a specific URL path and HTTP method.

**Examples**:

- "The POST /api/auth/signup endpoint handles user registration"
- "GET /api/todos endpoint returns the user's TODO list"

**Code References**:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/todos")
async def get_todos(current_user: User = Depends(get_current_user)):
    # Handler logic
    return {"data": todos}
```

### Pydantic Schema

**Definition**: A data validation and serialization model used to validate request bodies and serialize responses.

**Context**: FastAPI uses Pydantic for automatic validation, serialization, and API documentation generation.

**Examples**:

- "The TodoCreateSchema validates the TODO creation request"
- "Pydantic raises a validation error if required fields are missing"

**Code References**:

```python
from pydantic import BaseModel, EmailStr

class TodoCreateSchema(BaseModel):
    title: str
    description: str | None = None
    status: TodoStatus = TodoStatus.PENDING
    starts_date: datetime | None = None
    expires_date: datetime | None = None
    tag_ids: list[int] = []
```

### SQLAlchemy Model

**Definition**: A Python class that represents a database table using SQLAlchemy ORM.

**Context**: Models define the database schema and provide an object-oriented interface for database operations.

**Examples**:

- "The User model maps to the 'users' table"
- "Query TODOs using the SQLAlchemy model"

**Code References**:

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    todos = relationship("Todo", back_populates="user")
```

### Repository

**Definition**: A class that encapsulates database access logic for a specific entity, providing methods like get(), create(), update(), delete().

**Context**: Part of the Repository pattern in Clean Architecture. Separates business logic from data access.

**Examples**:

- "UserRepository.get_by_email() queries the database for a user"
- "TodoRepository.get_all_for_user() returns a user's TODO list"

**Code References**:

```python
class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def get_all_for_user(self, user_id: int) -> list[Todo]:
        return self.db.query(Todo).filter(Todo.user_id == user_id).all()
```

### Service

**Definition**: A class containing business logic that orchestrates operations across multiple repositories or handles complex workflows.

**Context**: Part of the Service layer in Clean Architecture. Services coordinate between the API layer and repository layer.

**Examples**:

- "AuthService.register_user() handles user registration logic"
- "TodoService.create_todo() validates input and calls TodoRepository"

**Code References**:

```python
class TodoService:
    def __init__(self, todo_repo: TodoRepository, tag_repo: TagRepository):
        self.todo_repo = todo_repo
        self.tag_repo = tag_repo

    async def create_todo(self, user_id: int, data: TodoCreateSchema) -> Todo:
        # Business logic, validation
        todo = self.todo_repo.create(user_id=user_id, **data.dict())
        return todo
```

### Dependency Injection

**Definition**: FastAPI's system for providing dependencies (like database sessions, current user) to endpoint handlers using Depends().

**Context**: Used to inject database sessions, authenticate users, and provide services to endpoints.

**Examples**:

- "Use Depends(get_db) to inject a database session"
- "Use Depends(get_current_user) to authenticate and get the current user"

**Code References**:

```python
from fastapi import Depends

@router.get("/api/todos")
async def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Endpoint logic
    pass
```

## Anti-Patterns (Terms to Avoid)

### ❌ "Task List"

**Use Instead**: TODO List, TODOs

**Reason**: "TODO" is our domain term; "task" is too generic and doesn't align with our domain model.

### ❌ "Category"

**Use Instead**: Tag

**Reason**: We specifically use "tag" for our flexible labeling system; "category" implies a rigid hierarchy.

### ❌ "Item"

**Use Instead**: TODO

**Reason**: Be specific about what kind of item. "TODO" is clear and domain-specific.

### ❌ "Login"

**Use Instead**: Sign In, Sign Out, Authentication

**Reason**: "Sign in" and "sign out" match our API endpoints (/api/auth/signin, /api/auth/signout); "login" is ambiguous.

## Usage Guidelines

### In Code

Use exact terminology from this document:

```python
# Good
todo: Todo = await todo_service.get_todo(todo_id)
user_todos = await todo_repository.get_all_for_user(user.id)
tags = await tag_repository.get_by_ids(tag_ids)

# Avoid
task = await task_service.get_task(task_id)
user_items = await item_repository.get_all_for_user(user.id)
categories = await category_repository.get_by_ids(category_ids)
```

### In API Endpoints

- Use `/api/todos` not `/api/tasks` or `/api/items`
- Use `/api/tags` not `/api/categories` or `/api/labels`
- Use `/api/auth/signin` not `/api/auth/login`

### In Documentation

- Always capitalize domain terms (User, TODO, Tag, Dashboard)
- Use consistent terminology across all docs
- Define terms on first use

### In Tests

Test names should use domain language:

```python
# Good
def test_user_can_create_todo_with_tags():
    # ...

def test_todo_filtering_by_tag_returns_correct_results():
    # ...

# Avoid
def test_user_can_create_task_with_categories():
    # ...

def test_item_filtering_by_label_returns_correct_results():
    # ...
```

## Glossary Quick Reference

| Term          | Definition                             | Code Type        |
| ------------- | -------------------------------------- | ---------------- |
| User          | Authenticated account holder           | `User`           |
| TODO          | Task owned by user                     | `Todo`           |
| Tag           | Label for categorizing TODOs           | `Tag`            |
| Dashboard     | Visual interface showing user's TODOs  | (client-side)    |
| Session       | Authenticated user connection          | `Session`        |
| TODO Status   | State of TODO (pending/progress/done)  | `TodoStatus`     |
| TodoTag       | Association between TODO and Tag       | `TodoTag`        |
| Date Range    | starts_date and expires_date           | `datetime` pairs |
| Color Code    | Hex color for tag visualization        | `str`            |
| Repository    | Data access layer class                | `*Repository`    |
| Service       | Business logic layer class             | `*Service`       |
| Endpoint      | FastAPI route handler                  | function         |

## Domain Rules

### Business Rules (Always True)

1. Each TODO belongs to exactly one User
2. A User can have zero or more TODOs
3. A TODO can have zero or more Tags
4. A Tag can be assigned to zero or more TODOs
5. Email addresses must be unique across all Users
6. TODO title is required (cannot be empty or null)
7. TODO status must be one of: pending, in_progress, completed
8. Color codes must be valid hex format (e.g., #RRGGBB)
9. Users can only access and modify their own TODOs
10. expires_date, if set, should be in the future (business logic, not enforced at DB level)

### Technical Rules (Always True)

1. All passwords are stored as bcrypt hashes, never plain text
2. All IDs are auto-incrementing integers (primary keys)
3. All timestamps stored as UTC datetime
4. Database operations requiring multiple updates use transactions
5. Session tokens are required for authentication on protected endpoints
6. Pydantic schemas validate all incoming request data
7. SQLAlchemy ORM handles all database queries (no raw SQL in application code)
8. Foreign key constraints enforced at database level

## Evolution of Language

This document is a living document. When new concepts are introduced:

1. **Discuss** the term with the team
2. **Define** it clearly with examples
3. **Document** it in this file
4. **Use** it consistently in code and conversation
5. **Refactor** old code to use new terminology when appropriate

### Change Log

**2024-02-07**: Initial version created

- Defined core entities: User, TODO, Tag
- Defined business concepts: Authentication, Authorization, TODO Status
- Established naming conventions for code, API, and documentation
- Documented domain and technical rules
