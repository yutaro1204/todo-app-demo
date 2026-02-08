"""
Unit tests for security utilities.
"""

from app.core.security import hash_password, verify_password, generate_token


def test_hash_password_returns_different_hash_each_time():
    """Test that hashing the same password produces different hashes (due to salting)."""
    password = "TestPassword123!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2
    assert len(hash1) > 0
    assert len(hash2) > 0


def test_verify_password_with_correct_password():
    """Test password verification with correct password."""
    password = "CorrectPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_with_wrong_password():
    """Test password verification with incorrect password."""
    password = "CorrectPassword123!"
    wrong_password = "WrongPassword123!"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_generate_token_returns_unique_tokens():
    """Test that token generation produces unique tokens."""
    token1 = generate_token()
    token2 = generate_token()

    assert token1 != token2
    assert len(token1) > 0
    assert len(token2) > 0
    # Tokens should be URL-safe
    assert "/" not in token1
    assert "+" not in token1
