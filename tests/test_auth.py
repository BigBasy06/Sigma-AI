# tests/test_auth.py
"""Tests for authentication routes and logic."""

import pytest

# from flask import session  # Not used directly in assertions anymore
from flask.testing import FlaskClient

# from flask_login import current_user # Not used directly in assertions

# Assuming User model and set_password exist
from flaskr.models import User

# from flaskr import db  # db fixture is injected via conftest


@pytest.fixture(scope="function")
def test_user(app, db):  # db fixture is injected via conftest
    """Fixture to create a test user."""
    # db here refers to the SQLAlchemy session fixture from conftest.py
    with app.app_context():
        user = User(user_identifier="testloginuser")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        # Return user id as creating it might detach it from session
        yield user.id
        # Teardown - clean up user if needed, though the db session fixture
        # from conftest should handle rollback.
        # user_obj = User.query.get(user.id)
        # if user_obj:
        #     db.session.delete(user_obj)
        #     db.session.commit()


def test_login_page_loads(client: FlaskClient):
    """Test that the login page loads correctly."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data  # Check for element in your login.html


def test_successful_login(client: FlaskClient, test_user):
    """Test logging in with correct credentials."""
    response = client.post(
        "/auth/login",
        data={"identifier": "testloginuser", "password": "password123"},
        follow_redirects=True,
    )  # follow_redirects to check final page
    assert response.status_code == 200
    assert b"Login successful!" in response.data  # Check flash message
    # Check if redirected to index (or wherever login redirects)
    assert b"Hello World from Sigma AI!" in response.data

    # Check session directly (less common, usually check behavior)
    # Ensure Flask-Login stores user_id as string
    with client.session_transaction() as flask_session:
        assert flask_session.get("_user_id") == str(test_user)


def test_login_invalid_identifier(client: FlaskClient):
    """Test login with a non-existent user identifier."""
    response = client.post(
        "/auth/login",
        data={"identifier": "nonexistentuser", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Check for the updated generic error message
    assert b"Invalid credentials." in response.data
    # Should stay on login page, not redirect
    assert b"Hello World from Sigma AI!" not in response.data


def test_login_incorrect_password(client: FlaskClient, test_user):
    """Test login with correct identifier but wrong password."""
    response = client.post(
        "/auth/login",
        data={"identifier": "testloginuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Check for the updated generic error message
    assert b"Invalid credentials." in response.data
    # Should stay on login page, not redirect
    assert b"Hello World from Sigma AI!" not in response.data


def test_logout(client: FlaskClient, test_user):
    """Test logging out after logging in."""
    # First, log in
    client.post(
        "/auth/login", data={"identifier": "testloginuser", "password": "password123"}
    )

    # Now, log out
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    assert b"Hello World from Sigma AI!" in response.data  # Should redirect to index

    # Verify session is cleared
    with client.session_transaction() as flask_session:
        assert "_user_id" not in flask_session


def test_login_required_decorator(client: FlaskClient):
    """Test accessing a protected route without logging in."""
    response = client.get("/auth/profile", follow_redirects=True)
    # Should redirect to login page
    assert response.status_code == 200
    assert b"Login" in response.data  # Assumes 'Login' text is on login page
    # Check for default Flask-Login flash message
    assert b"Please log in to access this page." in response.data


def test_access_protected_after_login(client: FlaskClient, test_user):
    """Test accessing protected route after successful login."""
    # Log in
    client.post(
        "/auth/login", data={"identifier": "testloginuser", "password": "password123"}
    )

    # Access protected route
    response = client.get("/auth/profile")
    assert response.status_code == 200
    # Check content of profile page
    assert b"Hello, testloginuser!" in response.data
    user_id_bytes = f"Your user ID is {test_user}".encode()
    assert user_id_bytes in response.data
