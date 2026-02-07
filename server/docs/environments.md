# Environments

This document describes the two primary workload environments for the TODO app demo server: Development (local machine) and Production (deployed).

## Environment Overview

| Aspect              | Development (Local)                              | Production (Deployed)                        |
| ------------------- | ------------------------------------------------ | -------------------------------------------- |
| **Purpose**         | Local development and testing                    | Live user-facing application                 |
| **Database**        | PostgreSQL in Docker                             | PostgreSQL (managed or self-hosted)          |
| **Server**          | Uvicorn with --reload (hot reload)               | Uvicorn with multiple workers                |
| **SSL**             | Not required                                     | Required (HTTPS)                             |
| **Logging**         | DEBUG level, console output                      | INFO level, file or centralized logging      |
| **Monitoring**      | Basic console logs                               | Production monitoring tools                  |
| **Process Manager** | Direct uvicorn command                           | Systemd, Supervisor, or Docker               |

---

## Development Environment (Local Machine)

### Purpose

The development environment runs entirely on a developer's local machine for:

- Feature development
- Bug fixes
- Local testing
- Database schema changes with Alembic
- Debugging

### Architecture

```
┌─────────────────────────────────────────┐
│     Developer's Local Machine           │
│  ┌─────────────────────────────────┐   │
│  │  FastAPI Application            │   │
│  │  (uvicorn --reload)             │   │
│  │  Port: 8000                     │   │
│  └─────────────────────────────────┘   │
│              ↕                          │
│  ┌─────────────────────────────────┐   │
│  │  PostgreSQL (Docker)            │   │
│  │  Port: 5432                     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Prerequisites

#### Required Software

- **Python 3.11+**: Programming language runtime
- **Poetry** or **pip**: Package management (Poetry recommended)
- **Docker Desktop**: For PostgreSQL container
- **Git**: Version control

#### Optional Tools

- **pgAdmin** or **DBeaver**: Visual database browser
- **Postman** or **Insomnia**: API testing tool
- **VS Code**: Recommended code editor with extensions:
  - Python
  - Pylance (type checking)
  - Ruff
  - Docker

### Setup Instructions

#### Quick Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd todoapp-server

# 2. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
# OR with Poetry:
poetry install

# 4. Start PostgreSQL
docker-compose up -d postgres

# 5. Copy environment variables
cp .env.example .env
# Edit .env with your values

# 6. Run database migrations
alembic upgrade head

# 7. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This will:

- Set up Python virtual environment
- Install all dependencies
- Start PostgreSQL in Docker
- Configure environment variables
- Apply database schema
- Start FastAPI server with hot reload

#### Manual Setup

If you prefer to set up manually:

#### 1. Clone Repository

```bash
git clone <repository-url>
cd todoapp-server
```

#### 2. Create Virtual Environment

```bash
# Using venv
python3.11 -m venv .venv
source .venv/bin/activate

# Using Poetry (alternative)
poetry shell
```

#### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Using Poetry
poetry install
```

#### 4. Start PostgreSQL Service

The `docker-compose.yml` file is provided in the project root. Start PostgreSQL:

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Or using docker-compose directly
docker-compose up -d

# View logs
docker-compose logs -f postgres
```

**Services included:**

- **PostgreSQL** on port 5432

**Health checks:** PostgreSQL includes health check to ensure it's ready before use.

Verify PostgreSQL is running:

```bash
# Check container status
docker-compose ps

# Test PostgreSQL connection
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_dev -c "SELECT 1;"
```

#### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

The `.env.example` file contains all necessary variables for local development with sensible defaults. Review and modify if needed:

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

#### 6. Set Up Database

```bash
# Apply database migrations
alembic upgrade head

# Optionally, seed initial data (if seed script exists)
python scripts/seed_data.py
```

#### 7. Start Development Server

```bash
# Start with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

- API documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Development Workflow

#### Daily Development

```bash
# Start PostgreSQL (if not running)
docker-compose up -d postgres

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start dev server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal: run tests in watch mode
pytest --watch  # If pytest-watch is installed
# Or manually:
pytest -v
```

**Features of development server:**

- **Hot Reload**: Automatically restarts when code changes
- **Interactive Docs**: `/docs` endpoint with Swagger UI
- **Detailed Errors**: Stack traces and debugging info
- **Fast Startup**: Optimized for quick iteration

#### Database Changes

```bash
# 1. Modify SQLAlchemy models in app/models/

# 2. Create migration
alembic revision --autogenerate -m "Add new field to todos"

# 3. Review the generated migration file in alembic/versions/

# 4. Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

#### View Database

```bash
# Using psql (PostgreSQL CLI)
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_dev

# Or connect with your preferred tool:
# Host: localhost
# Port: 5432
# Database: todoapp_dev
# User: todoapp
# Password: todoapp_dev_password
```

#### Stop Services

```bash
# Stop PostgreSQL (preserves data)
docker-compose stop

# Stop and remove containers (preserves data)
docker-compose down

# Stop and delete all data
docker-compose down -v
```

### Development Best Practices

1. **Never commit `.env`** - Contains sensitive credentials
2. **Use meaningful commit messages** - Follow Conventional Commits format
3. **Run tests before committing** - `pytest` to ensure nothing breaks
4. **Format code before committing** - `ruff format .` for consistent style
5. **Create migrations for schema changes** - Use `alembic revision --autogenerate`
6. **Keep dependencies updated** - Regularly update `requirements.txt` or `poetry.lock`
7. **Test API with Swagger UI** - Use `/docs` for quick API testing
8. **Check type hints** - Run `mypy app/` before committing
9. **Use virtual environment** - Always activate `.venv` before working

### Troubleshooting Development Environment

#### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_dev -c "SELECT version();"
```

#### Alembic Migration Issues

```bash
# Reset to specific migration
alembic downgrade <revision>

# Stamp database at current state (careful!)
alembic stamp head

# Generate new migration after fixing models
alembic revision --autogenerate -m "Fixed migration"
```

#### Port Conflicts

If port 8000 or 5432 is already in use:

```yaml
# Edit docker-compose.yml for PostgreSQL
services:
  postgres:
    ports:
      - '5433:5432' # Changed from 5432

# Update .env
DATABASE_URL=postgresql://todoapp:todoapp_dev_password@localhost:5433/todoapp_dev
```

For the application, use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

#### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Or with Poetry
poetry env remove python3.11
poetry install
```

---

## Production Environment

### Purpose

The production environment is for deployed applications serving real users. However, this TODO app demo server is **primarily designed for local development**.

If deploying to production, consider:

### Architecture

```
┌─────────────────────────────────────────┐
│          Production Server              │
│  ┌─────────────────────────────────┐   │
│  │  Nginx (Reverse Proxy)          │   │
│  │  Port: 80/443                   │   │
│  └─────────────────────────────────┘   │
│              ↕                          │
│  ┌─────────────────────────────────┐   │
│  │  Uvicorn Workers (4x)           │   │
│  │  Port: 8000                     │   │
│  └─────────────────────────────────┘   │
│              ↕                          │
│  ┌─────────────────────────────────┐   │
│  │  PostgreSQL                     │   │
│  │  Port: 5432                     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Production Configuration

**Environment Variables:**

```bash
# .env (Production)
APP_NAME="TODO App Demo Server"
DEBUG=false  # Important: disable debug mode

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/todoapp_prod

# Security
SECRET_KEY=<strong-random-secret-key>  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SESSION_EXPIRE_MINUTES=1440
BCRYPT_ROUNDS=12

# Server
HOST=0.0.0.0
PORT=8000

# CORS (adjust for your frontend)
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
```

### Running in Production

**Option 1: Direct Uvicorn (Simple)**

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Run with multiple workers
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --no-access-log
```

**Option 2: Systemd Service (Recommended)**

Create `/etc/systemd/system/todoapp.service`:

```ini
[Unit]
Description=TODO App Demo Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/todoapp
Environment="PATH=/var/www/todoapp/.venv/bin"
ExecStart=/var/www/todoapp/.venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable todoapp
sudo systemctl start todoapp

# Check status
sudo systemctl status todoapp

# View logs
sudo journalctl -u todoapp -f
```

**Option 3: Docker (Containerized)**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

```bash
# Build image
docker build -t todoapp-server .

# Run container
docker run -d \
  --name todoapp \
  -p 8000:8000 \
  --env-file .env \
  todoapp-server
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/todoapp
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/todoapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up HTTPS with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### Production Database

**PostgreSQL Setup:**

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE todoapp_prod;
CREATE USER todoapp WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE todoapp_prod TO todoapp;
\q

# Apply migrations
alembic upgrade head
```

**Backup Strategy:**

```bash
# Backup database
pg_dump -U todoapp todoapp_prod > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U todoapp todoapp_prod < backup_20240207.sql

# Automated daily backups with cron
0 2 * * * pg_dump -U todoapp todoapp_prod > /backups/todoapp_$(date +\%Y\%m\%d).sql
```

### Production Monitoring

**Logging:**

```python
# app/core/logging.py
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/todoapp/app.log'),
        logging.StreamHandler()
    ]
)
```

**Health Check Endpoint:**

```python
# app/api/health.py
from fastapi import APIRouter, status
from sqlalchemy import text
from app.db.database import SessionLocal

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connectivity
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
```

### Production Security Checklist

- [ ] DEBUG mode disabled (`DEBUG=false`)
- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled with valid SSL certificate
- [ ] CORS configured for specific origins only
- [ ] Database credentials secured
- [ ] `.env` file not committed to version control
- [ ] Regular security updates applied
- [ ] Firewall configured (only necessary ports open)
- [ ] Database backups automated
- [ ] Error messages don't expose sensitive information
- [ ] Rate limiting configured (if needed)
- [ ] SQL injection protection (using SQLAlchemy ORM)
- [ ] XSS protection (proper JSON serialization)

### Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Type checking passing (`mypy app/`)
- [ ] Code formatted (`ruff format .`)
- [ ] Database migrations created and reviewed
- [ ] Environment variables configured
- [ ] Dependencies up to date
- [ ] Security checklist completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Health check endpoint working
- [ ] Documentation updated

---

## Environment Variables Reference

### Application

- `APP_NAME`: Application name for logging and display
- `DEBUG`: Enable debug mode (true/false)

### Database

- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Example: `postgresql://todoapp:password@localhost:5432/todoapp_dev`

### Security

- `SECRET_KEY`: Secret key for session tokens (generate with `secrets.token_urlsafe(32)`)
- `SESSION_EXPIRE_MINUTES`: Session expiration time in minutes (default: 1440 = 24 hours)
- `BCRYPT_ROUNDS`: Number of bcrypt rounds for password hashing (default: 12)

### Server

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### CORS

- `ALLOWED_ORIGINS`: List of allowed origins for CORS (JSON array or comma-separated)

---

## Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: todoapp-postgres
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
    networks:
      - todoapp-network

volumes:
  postgres_data:

networks:
  todoapp-network:
    driver: bridge
```

Start services:

```bash
docker-compose up -d
```

Stop services:

```bash
docker-compose down
```

Stop and remove all data:

```bash
docker-compose down -v
```
