"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, status, HTTPException, Header
from app.schemas.auth import SignUpRequest, SignInRequest, SignInResponse, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    SessionNotFoundError,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    signup_data: SignUpRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new user account.

    Creates a new user with the provided email, name, and password.
    Password is automatically hashed before storage.

    Args:
        signup_data: User registration data (email, name, password)
        auth_service: AuthService dependency

    Returns:
        Created user information (without password)

    Raises:
        HTTPException 400: If email already exists
        HTTPException 422: If validation fails
    """
    try:
        user = auth_service.signup(
            email=signup_data.email,
            name=signup_data.name,
            password=signup_data.password,
        )
        return UserResponse.model_validate(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/signin", response_model=SignInResponse)
async def signin(
    signin_data: SignInRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Sign in to an existing user account.

    Authenticates user with email and password, then creates a new session.

    Args:
        signin_data: User login credentials (email, password)
        auth_service: AuthService dependency

    Returns:
        User information and session token

    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        user, token = auth_service.signin(
            email=signin_data.email,
            password=signin_data.password,
        )
        return SignInResponse(
            user=UserResponse.model_validate(user),
            token=token,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/signout", status_code=status.HTTP_200_OK)
async def signout(
    authorization: str = Header(..., description="Bearer token"),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Sign out from current session.

    Invalidates the session token provided in the Authorization header.

    Args:
        authorization: Authorization header (format: "Bearer {token}")
        auth_service: AuthService dependency

    Returns:
        Success message

    Raises:
        HTTPException 401: If token is invalid or not found
    """
    # Extract token from Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer {token}'",
        )

    token = authorization.replace("Bearer ", "")

    try:
        auth_service.signout(token)
        return {"message": "Successfully signed out"}
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
