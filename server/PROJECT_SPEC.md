# Server Project Specification Template

> **Instructions**: Fill in the essential information below. The skill will gather additional details from your codebase as needed.

---

## 1. Project Basics

- **Project Name**: TODO app demo server
- **Project Type**: Dashboard app for TODO
- **Description**: This application manages TODO of user. This project is in charge of the server side.
- **Core Problem Solved**: Organize TODO of user.

---

## 2. Technology Stack

### Backend

- **Framework**: FastAPI
- **Language**: Python
- **API Type**: REST
- **Database**: PostgreSQL
- **ORM/Query Builder**: SQLAlchemy
- **Authentication**: Session-based
- **Validation**: Pydantic

### Infrastructure & Services

- **Cache**: None
- **Message Queue**: None
- **Background Jobs**: None
- **Storage**: None
- **Search**: None
- **Container**: DockerCompose
- **Cloud/Hosting**: None(This is just demo project and supposed to be running only in local machine.)

### Observability

- **Logging**: Python logging
- **Monitoring**: None
- **Error Tracking**: None

### Testing & Tools

- **Unit/Integration Test**: Pytest
- **API Testing**: Postman
- **Package Manager**: pip

---

## 3. Key Features (3-5 main features)

1. User authentication and authorization
2. TODO list in dashboard which graphically displays existing TODOs
3. Filtering TODOs with tags
4. User profile configuration

---

## 4. Core API Flows (Top 2-3)

**Flow 1: User Registration**

1. Sign up with email and password
2. Sign in
3. Sign out

**Flow 2: Show and filter TODO**

1. Sign in
2. Show dashboard
3. Filter TODOs with tags

**Flow 3: Create TODO**

1. Sign in
2. Show dashboard
3. Create new TODO

**Flow 4: Update TODO**

1. Sign in
2. Show dashboard
3. Update existing TODO

**Flow 5: Delete TODO**

1. Sign in
2. Show dashboard
3. Delete existing TODO

---

## 5. Data Models (Top 3-5 entities)

1. **[User]**: id, email, name, password_hash, created_at, updated_at
3. **[Tag]**: id, name, color_code, created_at, updated_at
2. **[Todo]**: id, title, description, status, starts_date, expires_date, created_at, updated_at

---

## 6. API Endpoints (Top 5-10)

| Method | Path              | Description       | Auth? |
| ------ | ----------------- | ----------------- | ----- |
| POST   | `/api/auth/signup` | User signup        | No    |
| POST   | `/api/auth/signin` | User signin        | No    |
| POST   | `/api/auth/signout` | User signout        | No    |
| GET    | `/api/todos`   | List TODOs     | Yes    |
| GET    | `/api/todos/:id` | Get TODO     | Yes    |
| POST   | `/api/todos`     | Create TODO      | Yes   |
| PUT    | `/api/todos/:id` | Update TODO         | Yes   |
| DELETE    | `/api/todos/:id`  | DELETE TODO       | Yes   |

---

## 7. Domain Terminology (3-5 key terms)

1. **[User]**: Authenticated account holder
2. **[TODO]**: TODO belongs to User
3. **[Tag]**: Tag which TODO belongs to

---

## 8. Testing Strategy

- **Unit Test Coverage**: 80% business logic
- **Integration Tests**: All API endpoints
- **Load Testing**: Critical endpoints only
- **Testing Philosophy**: TDD

---

## 9. Backend Configuration

### API Design

- **API Style**: RESTful
- **API Versioning**:  URL-based /api/v1
- **Response Format**: JSON
- **Error Format**: RFC 7807
- **Pagination**: Offset-based

### Security

- **CORS Policy**: Specific origins, Wildcard for dev
- **Rate Limiting**: None
- **Input Validation**: Pydantic
- **HTTPS**: Required in production, but mainly this project is supposed to be running in local machine.
- **API Keys/Tokens**: Bearer tokens

### Data Processing

- **File Uploads**: None
- **Background Jobs**: None
- **Scheduled Tasks**: None
- **Webhooks**: None

### Database Strategy

- **Migration Strategy**: Manual
- **Seeding**: Manual
- **Backup**: None
- **Indexing Strategy**: Manual

---

## 10. Architecture Notes

**Why this stack?**
Python is easy for developer to use.
Basically these stacks are chosen because developers are familiarized with them.

**Key Constraints**:
No constraints so far

**Architecture Pattern**: Clean Architecture

---

## 11. Optional: Additional Information

### Third-Party Services (if used)

- **Auth**: None
- **Payment**: None
- **Email**: None
- **SMS**: None
- **Analytics**: None

### Non-Functional Requirements

- **Performance**: Not defined
- **Scalability**: Not defined
- **Availability**: Not defined
- **Security**: Auth required
- **Compliance**: None

### Deployment

- **CI/CD**: None
- **Deployment Strategy**: None
- **Environment Stages**: Development and Production, but mainly this project is supposed to be running in local machine.

---

**That's it!** The skill will use this information plus your codebase to generate comprehensive documentation.
