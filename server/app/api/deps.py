"""
Dependency functions for FastAPI endpoints.
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.todo_service import TodoService
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.todo_repository import TodoRepository
from app.core.exceptions import SessionNotFoundError, SessionExpiredError


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Dependency to create AuthService instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)
    return AuthService(user_repo, session_repo)


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Dependency to get the current authenticated user.

    Args:
        authorization: Authorization header (format: "Bearer {token}")
        auth_service: AuthService instance

    Returns:
        Current user instance

    Raises:
        HTTPException: 401 if token is invalid, missing, or expired
    """
    # Extract token from Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer {token}'",
        )

    token = authorization.replace("Bearer ", "")

    # Get user from token
    try:
        user = auth_service.get_current_user(token)
        return user
    except (SessionNotFoundError, SessionExpiredError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    """
    Dependency to create TodoService instance.

    Args:
        db: Database session

    Returns:
        TodoService instance
    """
    todo_repo = TodoRepository(db)
    return TodoService(todo_repo)
