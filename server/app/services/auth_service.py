"""
Authentication service for business logic.
"""

from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.models.user import User
from app.core.security import hash_password, verify_password, generate_token
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    SessionNotFoundError,
    SessionExpiredError,
)


class AuthService:
    """Service for authentication business logic."""

    def __init__(
        self, user_repo: UserRepository, session_repo: SessionRepository
    ) -> None:
        """
        Initialize AuthService.

        Args:
            user_repo: UserRepository instance
            session_repo: SessionRepository instance
        """
        self.user_repo = user_repo
        self.session_repo = session_repo

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
        """
        # Check if user already exists
        if self.user_repo.email_exists(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = self.user_repo.create(
            email=email, name=name, password_hash=password_hash
        )

        return user

    def signin(self, email: str, password: str) -> tuple[User, str]:
        """
        Authenticate user and create session.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (User instance, session token)

        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Get user by email
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        # Generate session token
        token = generate_token()

        # Create session
        self.session_repo.create(user_id=user.id, token=token)

        return user, token

    def signout(self, token: str) -> None:
        """
        Invalidate user session.

        Args:
            token: Session token to invalidate

        Raises:
            SessionNotFoundError: If token is not found
        """
        deleted = self.session_repo.delete(token)
        if not deleted:
            raise SessionNotFoundError("Session not found or already expired")

    def get_current_user(self, token: str) -> User:
        """
        Get current user from session token.

        Args:
            token: Session token

        Returns:
            User instance for the current session

        Raises:
            SessionNotFoundError: If token is not found
            SessionExpiredError: If session has expired
        """
        # Get session by token
        session = self.session_repo.get_by_token(token)
        if not session:
            raise SessionNotFoundError("Invalid or expired session token")

        # Check if session is expired
        if self.session_repo.is_expired(session):
            # Deactivate expired session
            self.session_repo.delete(token)
            raise SessionExpiredError("Session has expired")

        # Get user
        user = self.user_repo.get_by_id(session.user_id)
        if not user:
            raise SessionNotFoundError("User not found")

        return user
