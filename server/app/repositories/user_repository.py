"""
Repository for User data access.
"""

from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session) -> None:
        """
        Initialize UserRepository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            User instance if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User ID to search for

        Returns:
            User instance if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, name: str, password_hash: str) -> User:
        """
        Create a new user.

        Args:
            email: User's email address
            name: User's display name
            password_hash: Hashed password

        Returns:
            Created User instance
        """
        user = User(email=email, name=name, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None
