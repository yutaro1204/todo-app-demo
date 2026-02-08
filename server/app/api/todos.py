"""
Todo API endpoints.
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.schemas.todo import TodoResponse, TodoCreate
from app.services.todo_service import TodoService
from app.api.deps import get_current_user, get_todo_service
from app.models.user import User
from app.core.exceptions import TodoNotFoundError, UnauthorizedAccessError

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """
    Create a new TODO for the authenticated user.

    - **title**: TODO title (required, 1-200 chars)
    - **description**: Optional description (max 2000 chars)
    - **status**: TODO status (default: pending)
    - **starts_date**: Optional start date
    - **expires_date**: Optional expiration date (must be after starts_date)
    - **tag_ids**: Optional list of tag IDs to associate

    Returns the created TODO with generated ID and timestamps.
    """
    try:
        todo = todo_service.create_todo(current_user.id, todo_data)
        return todo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=list[TodoResponse])
async def list_todos(
    status_filter: str | None = Query(None, alias="status", description="Filter by status (pending, in_progress, completed)"),
    tag_ids: str | None = Query(None, description="Comma-separated tag IDs to filter by"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results (1-100)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> list[TodoResponse]:
    """
    List authenticated user's TODOs with optional filters.

    Supports filtering by:
    - status: pending, in_progress, or completed
    - tag_ids: comma-separated list of tag IDs (e.g., "1,2,3")
    - pagination: limit (max 100) and offset

    Returns TODOs ordered by created_at DESC (newest first).
    """
    # Parse tag_ids from comma-separated string to list[int]
    tag_id_list: list[int] | None = None
    if tag_ids:
        try:
            tag_id_list = [int(id.strip()) for id in tag_ids.split(",") if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Must be comma-separated integers (e.g., '1,2,3')",
            )

    # Get TODOs from service
    try:
        todos = todo_service.get_todos_for_user(
            user_id=current_user.id,
            status=status_filter,
            tag_ids=tag_id_list,
            limit=limit,
            offset=offset,
        )
        return todos
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
