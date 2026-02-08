# F001 - Auth System Implementation

**Status:** ✅ Completed (2026-02-08)
**Type:** Feature
**Priority:** High
**Coverage:** 91% overall (auth modules: 97% service, 100% security)
**Tests:** 26 passed (13 unit, 12 integration, 1 security)

## Objective

Implement user authentication system with signup, signin, and signout functionality. This is a foundational feature that enables user account management and secures access to TODO operations. The system uses session-based authentication with bcrypt password hashing.

## Context

This is the first core feature to be implemented for the TODO App Demo Server. Authentication is required before any TODO or Tag operations can be performed. The system must follow Clean Architecture patterns with clear separation between API, Service, and Repository layers.

Key domain concepts:
- **User**: Authenticated account holder with email, name, and hashed password
- **Sign Up**: User registration (NOT "signup" or "register")
- **Sign In**: User login (NOT "signin" or "login")
- **Sign Out**: User logout (NOT "signout" or "logout")

## Constraints

1. **Architecture**: Must follow Clean Architecture layers (API → Service → Repository → Models)
2. **Security**:
   - Passwords must be hashed using bcrypt with minimum 12 rounds
   - Session tokens must use `secrets.token_urlsafe(32)`
   - Never expose password_hash in responses
3. **Database**: Use SQLAlchemy ORM with PostgreSQL
4. **Validation**: Use Pydantic schemas for all request/response validation
5. **Type Safety**: All functions must have complete type hints
6. **Testing**: Minimum 90% coverage for authentication code (critical path)
7. **Naming**: Use project terminology (Sign In/Sign Out, not Login/Logout)
8. **API Paths**: `/api/auth/signup`, `/api/auth/signin`, `/api/auth/signout`

## Acceptance Criteria

- [x] User can sign up with email, name, and password
- [x] Email uniqueness is enforced at database level
- [x] Passwords are hashed with bcrypt (12+ rounds) before storage
- [x] User can sign in with email and password
- [x] Invalid credentials return 401 Unauthorized
- [x] Successful sign in returns session token and user info
- [x] Session token is stored in database with expiration (24 hours default)
- [x] User can sign out, which invalidates the session token
- [x] All endpoints return proper HTTP status codes (201, 200, 401, 400, 422)
- [x] Password validation enforces minimum security requirements
- [x] Email format validation is applied
- [x] Authorization dependency (`get_current_user`) is implemented for protected endpoints
- [x] Error handling covers duplicate emails, invalid credentials, expired sessions
- [x] Unit tests achieve >90% coverage for auth service (97% achieved)
- [x] Integration tests cover all three endpoints (signup, signin, signout)
- [x] Tests verify session creation, validation, and deletion
- [x] No password leaks in responses or logs

## Technical Approach

Implement authentication following Clean Architecture with four distinct layers:

### Layer 1: Models (app/models/)
Define SQLAlchemy ORM models for User and Session entities with proper relationships and constraints.

### Layer 2: Repositories (app/repositories/)
Create data access layer for User and Session operations (CRUD operations, no business logic).

### Layer 3: Services (app/services/)
Implement business logic for authentication, including password verification, session management, and validation.

### Layer 4: API (app/api/)
Create FastAPI endpoints with proper request/response handling, dependency injection, and error handling.

### Files to Create

#### Core Utilities
- `app/core/config.py` - Settings with Pydantic BaseSettings (SECRET_KEY, SESSION_EXPIRE_MINUTES, BCRYPT_ROUNDS)
- `app/core/security.py` - Password hashing utilities (hash_password, verify_password)
- `app/core/exceptions.py` - Custom exception classes (UserAlreadyExistsError, InvalidCredentialsError, etc.)

#### Database
- `app/db/database.py` - SQLAlchemy engine, SessionLocal, Base
- `alembic/env.py` - Alembic configuration
- `alembic/versions/001_create_users_table.py` - User table migration
- `alembic/versions/002_create_sessions_table.py` - Session table migration

#### Models
- `app/models/__init__.py` - Export all models
- `app/models/user.py` - User model (id, email, name, password_hash, created_at, updated_at)
- `app/models/session.py` - Session model (id, user_id, token, expires_at, created_at)

#### Schemas
- `app/schemas/__init__.py` - Export all schemas
- `app/schemas/auth.py` - SignUpRequest, SignInRequest, SignInResponse, UserResponse schemas

#### Repositories
- `app/repositories/__init__.py` - Export all repositories
- `app/repositories/user_repository.py` - UserRepository (get_by_email, get_by_id, create)
- `app/repositories/session_repository.py` - SessionRepository (create, get_by_token, delete)

#### Services
- `app/services/__init__.py` - Export all services
- `app/services/auth_service.py` - AuthService (signup, signin, signout, get_current_user)

#### API
- `app/api/__init__.py` - Export all routers
- `app/api/deps.py` - Dependency functions (get_db, get_current_user, get_auth_service)
- `app/api/auth.py` - Auth router with three endpoints

#### Main Application
- `app/main.py` - FastAPI app instance, CORS middleware, router registration
- `app/__init__.py` - Package initialization

#### Configuration
- `.env.example` - Environment variable template
- `docker-compose.yml` - PostgreSQL service for local development
- `alembic.ini` - Alembic configuration

### Files to Modify

None (this is the initial implementation).

### Dependencies

All dependencies should already be in requirements.txt per documentation:
- `fastapi ^0.104.0` - Web framework
- `uvicorn ^0.24.0` - ASGI server
- `sqlalchemy ^2.0.0` - ORM
- `alembic ^1.12.0` - Migrations
- `psycopg2-binary ^2.9.0` - PostgreSQL driver
- `pydantic ^2.5.0` - Validation
- `pydantic-settings ^2.1.0` - Settings management
- `passlib ^1.7.4` - Password hashing
- `bcrypt ^4.1.0` - Bcrypt backend
- `python-multipart ^0.0.6` - Form data parsing

## Testing Requirements

### Unit Tests (tests/unit/)

#### test_security.py
- `test_hash_password_returns_different_hash_each_time` - Verify bcrypt salting
- `test_verify_password_with_correct_password` - Valid password verification
- `test_verify_password_with_wrong_password` - Invalid password rejection
- `test_hash_password_uses_configured_rounds` - Verify bcrypt rounds setting

#### test_auth_service.py
- `test_signup_creates_user_with_hashed_password` - User creation logic
- `test_signup_raises_error_on_duplicate_email` - Email uniqueness enforcement
- `test_signin_returns_token_and_user_for_valid_credentials` - Sign in success path
- `test_signin_raises_error_for_invalid_email` - Non-existent user handling
- `test_signin_raises_error_for_invalid_password` - Wrong password handling
- `test_signout_deletes_session` - Session deletion
- `test_get_current_user_returns_user_for_valid_token` - Token validation
- `test_get_current_user_raises_error_for_invalid_token` - Invalid token handling
- `test_get_current_user_raises_error_for_expired_token` - Expired token handling

### Integration Tests (tests/integration/)

#### test_auth_api.py
- `test_signup_creates_user_in_database` - Full signup flow with DB
- `test_signup_returns_201_with_user_data` - Verify response format
- `test_signup_returns_400_for_duplicate_email` - Duplicate email error
- `test_signup_returns_422_for_invalid_email_format` - Validation error
- `test_signup_returns_422_for_weak_password` - Password validation
- `test_signin_returns_200_with_token_and_user` - Successful sign in
- `test_signin_returns_401_for_invalid_credentials` - Auth failure
- `test_signin_creates_session_in_database` - Verify session creation
- `test_signout_returns_200` - Successful sign out
- `test_signout_deletes_session_from_database` - Verify session deletion
- `test_signout_returns_401_for_invalid_token` - Unauthorized sign out attempt
- `test_protected_endpoint_requires_authentication` - Verify auth dependency works

### Test Fixtures (tests/conftest.py)
- `test_db` - Test database with clean state per test
- `client` - FastAPI TestClient
- `test_user` - Factory for creating test users
- `authenticated_client` - Client with valid auth token

### Coverage Goals
- Overall auth module: >90%
- Critical paths (password hashing, token validation): 100%
- All three API endpoints: 100%

## Documentation References

- **Functional Design**: `docs/functional-design.md` - Authentication flows, API specs (lines 6-75, 329-409)
- **Architecture**: `docs/architecture.md` - Clean Architecture patterns (lines 196-281), Security (lines 593-637)
- **Ubiquitous Language**: `docs/ubiquitous-language.md` - Terminology (Sign In/Sign Out, not Login/Logout)
- **Development Guidelines**: `docs/development-guidelines.md` - Coding standards, type hints, docstrings
- **Test Concepts**: `docs/test-concepts.md` - Testing strategy, fixtures, coverage requirements
- **Repository Structure**: `docs/repository-structure.md` - Directory organization, file naming

## Implementation Notes

### Session Management
- Sessions stored in database (not in-memory) for scalability
- Session tokens are secure random strings (32 bytes, URL-safe)
- Expired sessions should be cleaned up (can be done via scheduled task later)
- Consider adding created_at index on sessions table for cleanup queries

### Password Requirements
Enforce via Pydantic validator:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Error Handling Strategy
- Use custom exceptions in service layer (UserAlreadyExistsError, InvalidCredentialsError)
- Map to HTTP exceptions in API layer via exception handlers
- Never expose internal details in error messages
- Log authentication failures for security monitoring

### Security Considerations
- Use constant-time comparison for tokens to prevent timing attacks
- Implement rate limiting for sign in attempts (future enhancement)
- Consider adding CSRF protection if using cookie-based sessions
- Log all authentication events (signup, signin, signout, failures)
- Never log passwords or tokens

### Implementation Order
1. Set up core utilities (config, security, exceptions)
2. Create database models and migrations
3. Implement repositories (data access)
4. Implement auth service (business logic)
5. Create API endpoints with dependencies
6. Write unit tests alongside implementation
7. Write integration tests
8. Verify >90% coverage
9. Manual testing with Swagger UI at http://localhost:8000/docs

### Type Hints Example
```python
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, db: Session) -> None:
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

### Docstring Example (Google Style)
```python
def signup(self, email: str, name: str, password: str) -> User:
    """
    Create a new user account with hashed password.

    Args:
        email: User's email address (must be unique)
        name: User's display name
        password: Plain text password (will be hashed)

    Returns:
        Created User instance with hashed password

    Raises:
        UserAlreadyExistsError: If email is already registered
        ValueError: If password doesn't meet requirements
    """
```
