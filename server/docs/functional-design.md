# Functional Design

## Architecture for Each Function

### 1. Authentication System

#### Sign Up

**Flow:**

1. User submits email, name, and password via POST /api/auth/signup
2. Server validates input using Pydantic schema
3. Check if email already exists in database
4. Hash password using bcrypt
5. Create new user record in database
6. Return success response with user information
7. User can now sign in

**Components:**

- `POST /api/auth/signup` endpoint
- `UserCreateSchema` Pydantic model for validation
- `AuthService` for business logic
- `UserRepository` for database operations
- `PasswordHasher` utility for bcrypt operations

**Data Flow:**

```
Request (email, name, password) → Pydantic validation → AuthService →
Password hashing → UserRepository → PostgreSQL → Response (user_id, email, name)
```

#### Sign In

**Flow:**

1. User submits email and password via POST /api/auth/signin
2. Server validates input format
3. Look up user by email in database
4. Verify password hash matches
5. Create session token
6. Store session in database or cache
7. Return session token to client
8. Client includes token in subsequent requests

**Components:**

- `POST /api/auth/signin` endpoint
- `UserLoginSchema` Pydantic model
- `AuthService` for authentication logic
- `SessionManager` for session handling
- `PasswordHasher` for verification

**Data Flow:**

```
Request (email, password) → UserRepository → Password verification →
Session creation → Response (session_token, user_info)
```

#### Sign Out

**Flow:**

1. User sends POST /api/auth/signout with session token
2. Server validates session token
3. Delete session from storage
4. Return success response

**Components:**

- `POST /api/auth/signout` endpoint
- `SessionManager` for session deletion
- Authentication middleware

### 2. TODO Management System

#### Create TODO

**Flow:**

1. Authenticated user sends POST /api/todos with TODO data
2. Server validates authentication token
3. Validate TODO data (title required, optional description, dates, tags)
4. Create TODO record associated with user
5. Associate tags if provided
6. Return created TODO with ID
7. Dashboard updates with new TODO

**Components:**

- `POST /api/todos` endpoint
- `TodoCreateSchema` Pydantic model
- `TodoService` for business logic
- `TodoRepository` for database operations
- Authentication middleware

#### List TODOs

**Flow:**

1. Authenticated user sends GET /api/todos with optional filters
2. Parse query parameters (tag filters, status, dates)
3. Query database with filters applied
4. Return list of TODOs with pagination
5. Include associated tag information
6. Dashboard displays filtered TODOs

**Components:**

- `GET /api/todos` endpoint
- `TodoQueryParams` Pydantic model
- `TodoService` for filtering logic
- `TodoRepository` for queries

#### Get Single TODO

**Flow:**

1. User sends GET /api/todos/{id}
2. Verify user owns the TODO
3. Fetch TODO with all associated data (tags)
4. Return complete TODO information

**Components:**

- `GET /api/todos/{id}` endpoint
- `TodoService` for authorization check
- `TodoRepository` for data retrieval

#### Update TODO

**Flow:**

1. User sends PUT /api/todos/{id} with updated data
2. Verify user owns the TODO
3. Validate update data
4. Update TODO record in database
5. Update associated tags if changed
6. Update updated_at timestamp
7. Return updated TODO

**Components:**

- `PUT /api/todos/{id}` endpoint
- `TodoUpdateSchema` Pydantic model
- `TodoService` for update logic
- `TodoRepository` for database update

#### Delete TODO

**Flow:**

1. User sends DELETE /api/todos/{id}
2. Verify user owns the TODO
3. Delete TODO from database (cascade deletes tag associations)
4. Return success response

**Components:**

- `DELETE /api/todos/{id}` endpoint
- `TodoService` for authorization and deletion
- `TodoRepository` for database deletion

### 3. Tag Management System

#### Create Tag

**Flow:**

1. User creates tag with name and color_code
2. Validate tag data (name required, color_code format)
3. Check for duplicate tag names for user
4. Create tag record
5. Return created tag with ID

**Components:**

- Tag creation endpoint (part of TODO or separate)
- `TagCreateSchema` Pydantic model
- `TagService` for tag logic
- `TagRepository` for database operations

#### Filter by Tags

**Flow:**

1. User selects tags in dashboard UI
2. Frontend sends GET /api/todos?tags=tag1,tag2
3. Server queries TODOs having ANY or ALL specified tags
4. Return filtered TODO list
5. Dashboard updates to show only matching TODOs

**Components:**

- Query parameter parsing in GET /api/todos
- `TodoRepository` with tag filtering logic
- SQLAlchemy JOIN queries for tag relationships

## System Structure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                  (Separate frontend project)                 │
│              HTTP requests to REST API endpoints             │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server Layer                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes (app/api/)                                │  │
│  │  ├── /api/auth/signup, /signin, /signout             │  │
│  │  ├── /api/todos (GET, POST)                          │  │
│  │  ├── /api/todos/{id} (GET, PUT, DELETE)              │  │
│  │  └── Authentication Middleware                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services Layer (app/services/)                       │  │
│  │  ├── AuthService                                      │  │
│  │  ├── TodoService                                      │  │
│  │  ├── TagService                                       │  │
│  │  └── Business logic and validation                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Repositories (app/repositories/)                     │  │
│  │  ├── UserRepository                                   │  │
│  │  ├── TodoRepository                                   │  │
│  │  └── TagRepository                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────┐
│                         Data Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                                  │  │
│  │  ├── users table                                      │  │
│  │  ├── todos table                                      │  │
│  │  ├── tags table                                       │  │
│  │  └── todo_tags association table                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Model Definition

### Core Entities

#### User

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User:
    id: int  # Primary key, auto-increment
    email: str  # Unique, not null, indexed
    name: str  # User's display name
    password_hash: str  # Bcrypt hashed password, never exposed
    created_at: datetime  # Timestamp of registration
    updated_at: datetime  # Last profile update

    # Relationships
    todos: List[Todo]  # One-to-many with Todo
```

#### Todo

```python
class Todo:
    id: int  # Primary key, auto-increment
    user_id: int  # Foreign key to User, not null, indexed
    title: str  # TODO title, required, max 200 chars
    description: str | None  # Optional detailed description
    status: TodoStatus  # Enum: pending, in_progress, completed
    starts_date: datetime | None  # Optional start date
    expires_date: datetime | None  # Optional deadline
    created_at: datetime  # Creation timestamp
    updated_at: datetime  # Last modification timestamp

    # Relationships
    user: User  # Many-to-one with User
    tags: List[Tag]  # Many-to-many with Tag through todo_tags

from enum import Enum

class TodoStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
```

#### Tag

```python
class Tag:
    id: int  # Primary key, auto-increment
    name: str  # Tag name, required, max 50 chars
    color_code: str  # Hex color code (e.g., #FF5733), max 7 chars
    created_at: datetime  # Creation timestamp
    updated_at: datetime  # Last modification timestamp

    # Relationships
    todos: List[Todo]  # Many-to-many with Todo through todo_tags
```

#### TodoTag (Association Table)

```python
class TodoTag:
    id: int  # Primary key
    todo_id: int  # Foreign key to Todo
    tag_id: int  # Foreign key to Tag
    created_at: datetime  # When tag was assigned

    # Composite unique constraint on (todo_id, tag_id)
```

### Database Relationships

```
User (1) ──< (N) Todo
Todo (N) ──< (N) Tag [through todo_tags]
```

## API Design

### Authentication Endpoints

#### POST /api/auth/signup

**Request:**

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2024-02-07T10:30:00Z"
    }
  }
}
```

**Errors:**

- 400: Email already exists or validation failed
- 422: Invalid input format

#### POST /api/auth/signin

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "session_token_here"
  }
}
```

**Errors:**

- 401: Invalid credentials
- 422: Invalid input format

#### POST /api/auth/signout

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Signed out successfully"
}
```

### TODO Endpoints

#### GET /api/todos

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**

- `status` (optional: pending, in_progress, completed)
- `tags` (optional: comma-separated tag IDs or names)
- `page` (default: 1)
- `limit` (default: 50)

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "todos": [
      {
        "id": 1,
        "title": "Complete project documentation",
        "description": "Write comprehensive docs for the API",
        "status": "in_progress",
        "starts_date": "2024-02-01T00:00:00Z",
        "expires_date": "2024-02-15T23:59:59Z",
        "tags": [
          {
            "id": 1,
            "name": "work",
            "color_code": "#FF5733"
          },
          {
            "id": 2,
            "name": "urgent",
            "color_code": "#C70039"
          }
        ],
        "created_at": "2024-02-01T10:00:00Z",
        "updated_at": "2024-02-07T09:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 42,
      "items_per_page": 50
    }
  }
}
```

#### GET /api/todos/:id

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "status": "in_progress",
    "starts_date": "2024-02-01T00:00:00Z",
    "expires_date": "2024-02-15T23:59:59Z",
    "tags": [
      {
        "id": 1,
        "name": "work",
        "color_code": "#FF5733"
      }
    ],
    "created_at": "2024-02-01T10:00:00Z",
    "updated_at": "2024-02-07T09:30:00Z"
  }
}
```

**Errors:**

- 404: TODO not found
- 403: TODO belongs to different user

#### POST /api/todos

**Headers:** `Authorization: Bearer {token}`

**Request:**

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, vegetables",
  "status": "pending",
  "starts_date": "2024-02-08T00:00:00Z",
  "expires_date": "2024-02-10T18:00:00Z",
  "tag_ids": [3, 5]
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": 10,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, vegetables",
    "status": "pending",
    "starts_date": "2024-02-08T00:00:00Z",
    "expires_date": "2024-02-10T18:00:00Z",
    "tags": [
      {
        "id": 3,
        "name": "personal",
        "color_code": "#28B463"
      },
      {
        "id": 5,
        "name": "shopping",
        "color_code": "#3498DB"
      }
    ],
    "created_at": "2024-02-07T11:00:00Z",
    "updated_at": "2024-02-07T11:00:00Z"
  }
}
```

**Errors:**

- 400: Validation failed (missing title, invalid dates, etc.)
- 422: Invalid input format

#### PUT /api/todos/:id

**Headers:** `Authorization: Bearer {token}`

**Request:**

```json
{
  "title": "Buy groceries (updated)",
  "status": "completed",
  "tag_ids": [3]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 10,
    "title": "Buy groceries (updated)",
    "description": "Milk, eggs, bread, vegetables",
    "status": "completed",
    "starts_date": "2024-02-08T00:00:00Z",
    "expires_date": "2024-02-10T18:00:00Z",
    "tags": [
      {
        "id": 3,
        "name": "personal",
        "color_code": "#28B463"
      }
    ],
    "created_at": "2024-02-07T11:00:00Z",
    "updated_at": "2024-02-08T15:30:00Z"
  }
}
```

**Errors:**

- 404: TODO not found
- 403: TODO belongs to different user
- 400: Validation failed

#### DELETE /api/todos/:id

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**

```json
{
  "success": true,
  "message": "TODO deleted successfully"
}
```

**Errors:**

- 404: TODO not found
- 403: TODO belongs to different user

### Tag Endpoints (Optional, may be managed through TODOs)

#### GET /api/tags

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "id": 1,
        "name": "work",
        "color_code": "#FF5733"
      },
      {
        "id": 2,
        "name": "personal",
        "color_code": "#28B463"
      }
    ]
  }
}
```

#### POST /api/tags

**Headers:** `Authorization: Bearer {token}`

**Request:**

```json
{
  "name": "urgent",
  "color_code": "#C70039"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "urgent",
    "color_code": "#C70039",
    "created_at": "2024-02-07T12:00:00Z",
    "updated_at": "2024-02-07T12:00:00Z"
  }
}
```
