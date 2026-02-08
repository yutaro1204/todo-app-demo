"""
Integration tests for authentication API endpoints.
"""

from app.models.user import User
from app.models.session import Session


def test_signup_creates_user_in_database(client, test_db):
    """Test full signup flow creates user in database."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "NewPass123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data

    # Verify user exists in database
    user = test_db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.name == "New User"


def test_signup_returns_400_for_duplicate_email(client, test_user):
    """Test signup fails with 400 for duplicate email."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "testuser@example.com",  # Already exists
            "name": "Another User",
            "password": "Pass123!",
        },
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_signup_returns_422_for_invalid_email_format(client):
    """Test signup validation rejects invalid email format."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "not-an-email",
            "name": "User",
            "password": "Pass123!",
        },
    )

    assert response.status_code == 422


def test_signup_returns_422_for_weak_password(client):
    """Test signup validation rejects weak password."""
    # Missing uppercase
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "name": "User",
            "password": "weakpass123!",
        },
    )
    assert response.status_code == 422

    # Missing special character
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "name": "User",
            "password": "WeakPass123",
        },
    )
    assert response.status_code == 422

    # Too short
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "name": "User",
            "password": "Pass1!",
        },
    )
    assert response.status_code == 422


def test_signin_returns_200_with_token_and_user(client, test_user):
    """Test successful signin returns token and user info."""
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "testuser@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["name"] == "Test User"
    assert len(data["token"]) > 0
    assert "password" not in data["user"]


def test_signin_returns_401_for_invalid_credentials(client, test_user):
    """Test signin fails with 401 for wrong password."""
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "testuser@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_signin_returns_401_for_nonexistent_email(client):
    """Test signin fails with 401 for nonexistent email."""
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401


def test_signin_creates_session_in_database(client, test_user, test_db):
    """Test signin creates session in database."""
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "testuser@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 200
    token = response.json()["token"]

    # Verify session exists in database
    session = test_db.query(Session).filter(Session.token == token).first()
    assert session is not None
    assert session.user_id == test_user.id
    assert session.is_active is True


def test_signout_returns_200(authenticated_client):
    """Test successful signout."""
    response = authenticated_client.post("/api/auth/signout")

    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()


def test_signout_deletes_session_from_database(authenticated_client, test_db):
    """Test signout deactivates session in database."""
    # Extract token from client headers
    token = authenticated_client.headers["Authorization"].replace("Bearer ", "")

    # Verify session exists and is active
    session_before = test_db.query(Session).filter(Session.token == token).first()
    assert session_before is not None
    assert session_before.is_active is True

    # Sign out
    response = authenticated_client.post("/api/auth/signout")
    assert response.status_code == 200

    # Verify session is deactivated
    test_db.expire_all()  # Refresh from database
    session_after = test_db.query(Session).filter(Session.token == token).first()
    assert session_after.is_active is False


def test_signout_returns_401_for_invalid_token(client):
    """Test signout fails with 401 for invalid token."""
    response = client.post(
        "/api/auth/signout",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401


def test_protected_endpoint_requires_authentication(client):
    """Test that protected endpoints require authentication."""
    # This will be useful when we add protected endpoints
    # For now, test that signout requires authentication
    response = client.post("/api/auth/signout")

    assert response.status_code == 422  # Missing Authorization header
