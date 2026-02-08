"""
Pydantic schemas for authentication requests and responses.
"""

import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr


class SignUpRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(
        ..., min_length=1, max_length=255, description="User's display name"
    )
    password: str = Field(
        ..., min_length=8, max_length=255, description="User's password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password meets security requirements.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            v: Password string

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v


class SignInRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SignInResponse(BaseModel):
    """Response schema for successful sign in."""

    user: UserResponse
    token: str = Field(..., description="Session token for authentication")
