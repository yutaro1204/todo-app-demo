"""API routers and endpoints."""

from app.api.auth import router as auth_router
from app.api.todos import router as todos_router

__all__ = ["auth_router", "todos_router"]
