"""
Repository for Session data access.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.core.config import settings


class SessionRepository:
    """Repository for Session database operations."""

    def __init__(self, db: DBSession) -> None:
        """
        Initialize SessionRepository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, user_id: int, token: str) -> Session:
        """
        Create a new session.

        Args:
            user_id: User ID for the session
            token: Session token

        Returns:
            Created Session instance
        """
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.SESSION_EXPIRE_MINUTES
        )
        session = Session(
            user_id=user_id, token=token, expires_at=expires_at, is_active=True
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_token(self, token: str) -> Session | None:
        """
        Get session by token.

        Args:
            token: Session token to search for

        Returns:
            Session instance if found, None otherwise
        """
        return (
            self.db.query(Session)
            .filter(Session.token == token, Session.is_active.is_(True))
            .first()
        )

    def delete(self, token: str) -> bool:
        """
        Delete (deactivate) a session by token.

        Args:
            token: Session token to delete

        Returns:
            True if session was deleted, False if not found
        """
        session = self.get_by_token(token)
        if session:
            session.is_active = False
            self.db.commit()
            return True
        return False

    def delete_expired(self) -> int:
        """
        Delete all expired sessions.

        Returns:
            Number of sessions deleted
        """
        now = datetime.utcnow()
        result = (
            self.db.query(Session)
            .filter(Session.expires_at < now, Session.is_active.is_(True))
            .update({"is_active": False})
        )
        self.db.commit()
        return result

    def is_expired(self, session: Session) -> bool:
        """
        Check if a session is expired.

        Args:
            session: Session to check

        Returns:
            True if expired, False otherwise
        """
        return datetime.utcnow() > session.expires_at
