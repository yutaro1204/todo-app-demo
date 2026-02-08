"""
Unit tests for AuthService.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.models.user import User
from app.models.session import Session
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    SessionNotFoundError,
    SessionExpiredError,
)
from app.core.security import hash_password


@pytest.fixture
def mock_user_repo():
    """Mock UserRepository."""
    return Mock()


@pytest.fixture
def mock_session_repo():
    """Mock SessionRepository."""
    return Mock()


@pytest.fixture
def auth_service(mock_user_repo, mock_session_repo):
    """AuthService with mocked repositories."""
    return AuthService(mock_user_repo, mock_session_repo)


def test_signup_creates_user_with_hashed_password(auth_service, mock_user_repo):
    """Test successful user creation with hashed password."""
    # Arrange
    mock_user_repo.email_exists.return_value = False
    mock_user = User(id=1, email="new@example.com", name="New User")
    mock_user_repo.create.return_value = mock_user

    # Act
    user = auth_service.signup("new@example.com", "New User", "Password123!")

    # Assert
    assert user.id == 1
    assert user.email == "new@example.com"
    mock_user_repo.email_exists.assert_called_once_with("new@example.com")
    mock_user_repo.create.assert_called_once()
    # Verify password was hashed (not stored as plain text)
    call_args = mock_user_repo.create.call_args[1]
    assert call_args["password_hash"] != "Password123!"


def test_signup_raises_error_on_duplicate_email(auth_service, mock_user_repo):
    """Test signup fails when email already exists."""
    # Arrange
    mock_user_repo.email_exists.return_value = True

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError):
        auth_service.signup("existing@example.com", "User", "Password123!")


def test_signin_returns_token_and_user_for_valid_credentials(
    auth_service, mock_user_repo, mock_session_repo
):
    """Test successful sign in with valid credentials."""
    # Arrange
    password_hash = hash_password("Password123!")
    mock_user = User(id=1, email="user@example.com", password_hash=password_hash)
    mock_user_repo.get_by_email.return_value = mock_user

    mock_session = Session(id=1, user_id=1, token="test_token")
    mock_session_repo.create.return_value = mock_session

    # Act
    user, token = auth_service.signin("user@example.com", "Password123!")

    # Assert
    assert user.id == 1
    assert token is not None
    mock_user_repo.get_by_email.assert_called_once_with("user@example.com")
    mock_session_repo.create.assert_called_once()


def test_signin_raises_error_for_invalid_email(auth_service, mock_user_repo):
    """Test signin fails for non-existent email."""
    # Arrange
    mock_user_repo.get_by_email.return_value = None

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.signin("nonexistent@example.com", "Password123!")


def test_signin_raises_error_for_invalid_password(auth_service, mock_user_repo):
    """Test signin fails for incorrect password."""
    # Arrange
    password_hash = hash_password("CorrectPassword123!")
    mock_user = User(id=1, email="user@example.com", password_hash=password_hash)
    mock_user_repo.get_by_email.return_value = mock_user

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.signin("user@example.com", "WrongPassword123!")


def test_signout_deletes_session(auth_service, mock_session_repo):
    """Test signout successfully deletes session."""
    # Arrange
    mock_session_repo.delete.return_value = True

    # Act
    auth_service.signout("valid_token")

    # Assert
    mock_session_repo.delete.assert_called_once_with("valid_token")


def test_signout_raises_error_for_invalid_token(auth_service, mock_session_repo):
    """Test signout fails for invalid token."""
    # Arrange
    mock_session_repo.delete.return_value = False

    # Act & Assert
    with pytest.raises(SessionNotFoundError):
        auth_service.signout("invalid_token")


def test_get_current_user_returns_user_for_valid_token(
    auth_service, mock_user_repo, mock_session_repo
):
    """Test getting current user with valid token."""
    # Arrange
    mock_session = Session(
        id=1,
        user_id=1,
        token="valid_token",
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    mock_session_repo.get_by_token.return_value = mock_session
    mock_session_repo.is_expired.return_value = False

    mock_user = User(id=1, email="user@example.com")
    mock_user_repo.get_by_id.return_value = mock_user

    # Act
    user = auth_service.get_current_user("valid_token")

    # Assert
    assert user.id == 1
    mock_session_repo.get_by_token.assert_called_once_with("valid_token")
    mock_user_repo.get_by_id.assert_called_once_with(1)


def test_get_current_user_raises_error_for_invalid_token(
    auth_service, mock_session_repo
):
    """Test getting current user fails for invalid token."""
    # Arrange
    mock_session_repo.get_by_token.return_value = None

    # Act & Assert
    with pytest.raises(SessionNotFoundError):
        auth_service.get_current_user("invalid_token")


def test_get_current_user_raises_error_for_expired_token(
    auth_service, mock_session_repo
):
    """Test getting current user fails for expired token."""
    # Arrange
    mock_session = Session(
        id=1,
        user_id=1,
        token="expired_token",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    mock_session_repo.get_by_token.return_value = mock_session
    mock_session_repo.is_expired.return_value = True

    # Act & Assert
    with pytest.raises(SessionExpiredError):
        auth_service.get_current_user("expired_token")

    # Verify expired session was deleted
    mock_session_repo.delete.assert_called_once_with("expired_token")
