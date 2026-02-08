"""
Custom exception classes for application-specific errors.
"""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""

    pass


class InvalidCredentialsError(Exception):
    """Raised when authentication credentials are invalid."""

    pass


class SessionNotFoundError(Exception):
    """Raised when a session token is not found or invalid."""

    pass


class SessionExpiredError(Exception):
    """Raised when a session token has expired."""

    pass


class UnauthorizedError(Exception):
    """Raised when user is not authorized to perform an action."""

    pass


class TodoNotFoundError(Exception):
    """Raised when a TODO is not found."""

    pass


class UnauthorizedAccessError(Exception):
    """Raised when user attempts to access a resource they don't own."""

    pass
