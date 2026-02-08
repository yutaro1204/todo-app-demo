"""
Pytest fixtures for testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """
    Create a test client with test database.
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """
    Create a test user in the database.
    """
    user = User(
        email="testuser@example.com",
        name="Test User",
        password_hash=hash_password("TestPass123!"),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Create an authenticated test client with a valid session token.
    """
    # Sign in to get a token
    response = client.post(
        "/api/auth/signin",
        json={"email": "testuser@example.com", "password": "TestPass123!"},
    )
    token = response.json()["token"]

    # Add authorization header to client
    client.headers = {"Authorization": f"Bearer {token}"}

    return client
