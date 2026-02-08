# Steering Files

This directory contains steering files for guiding implementation tasks.

## Active Features

None yet.

## Active Bugs

None yet.

## Active Refactoring

None yet.

## Completed

### Features
- **[F003: Create TODO API](features/F003-create-todo-api.md)** ✅ Completed (2026-02-08)
  - Status: All 16 acceptance criteria met
  - Leveraged: Existing models, schemas, repository, service from F002
  - Tests: 17 new integration tests
  - Endpoint: POST /api/todos with full validation
  - Features: Title/description validation, date validation, tag support, 201 Created response

- **[F002: List TODOs API](features/F002-list-todos-api.md)** ✅ Completed (2026-02-08)
  - Status: All 14 acceptance criteria met
  - Models: Todo, Tag, TodoTag with database migration
  - Tests: 40 passed (21 unit + 19 integration)
  - Endpoint: GET /api/todos with filtering and pagination
  - Features: Status filter, tag filter, pagination, eager loading

- **[F001: Auth System Implementation](features/F001-auth-system-implementation.md)** ✅ Completed (2026-02-08)
  - Status: All 18 acceptance criteria met
  - Coverage: 91% overall (97% auth service, 100% security)
  - Tests: 26 passed (13 unit + 12 integration + 1 security)
  - Endpoints: POST /api/auth/signup, /signin, /signout

## Usage

Use the `/create-steering-file` skill to create new steering files, and `/implement-steering-file` to implement them.
