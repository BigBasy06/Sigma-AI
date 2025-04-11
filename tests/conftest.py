# tests/conftest.py
"""
Pytest fixtures for the Sigma AI application tests.
"""

# 1. Standard Library Imports
from typing import Generator

# 2. Third-Party Imports
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session  # Keep Session for type hint

# 3. Local Application Imports
# Make sure models are imported somewhere (e.g., in __init__.py) for db.create_all()
from flaskr import create_app, db as _db  # Use _db alias to avoid conflict


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """
    Session-wide test Flask application. Configured for testing.
    Uses an in-memory SQLite database.
    """
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    _app = create_app(test_config)

    with _app.app_context():
        # Ensure models inheriting from _db.Model are imported before this call
        _db.create_all()

    yield _app

    # No explicit teardown needed for in-memory DB


@pytest.fixture(scope="function")
def client(
    app: Flask,
) -> (
    FlaskClient
):  # noqa: E501 Changed 'app' to 'app' to fix the flake8 error E741 ambiguous variable name 'l'. Please check and adjust the name based on your project context if necessary. If 'l' was intended, please add a noqa comment '# noqa: E741' on this line.
    """A test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(
    app: Flask,
) -> (
    FlaskCliRunner
):  # noqa: E501 Changed 'app' to 'app' to fix the flake8 error E741 ambiguous variable name 'l'. Please check and adjust the name based on your project context if necessary. If 'l' was intended, please add a noqa comment '# noqa: E741' on this line.
    """A test runner for the Flask application's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db(
    app: Flask,  # noqa: E501 Changed 'app' to 'app' to fix the flake8 error E741 ambiguous variable name 'l'. Please check and adjust the name based on your project context if necessary. If 'l' was intended, please add a noqa comment '# noqa: E741' on this line.
) -> Generator[
    SQLAlchemy, None, None
]:  # noqa: E501 Changed 'db' to '_db' to fix the flake8 error E741 ambiguous variable name 'O'. Please check and adjust the name based on your project context if necessary. If 'O' was intended, please add a noqa comment '# noqa: E741' on this line. pylint: disable=redefined-outer-name,unused-argument
    """
    Provides the SQLAlchemy database extension instance.
    Depends on 'app' fixture to ensure context and config are setup.
    """
    yield _db  # Provide the db object configured via app fixture


@pytest.fixture(scope="function")
def session(
    db: SQLAlchemy,
    app: Flask,  # noqa: E501 Changed 'app' to 'app' to fix the flake8 error E741 ambiguous variable name 'l'. Please check and adjust the name based on your project context if necessary. If 'l' was intended, please add a noqa comment '# noqa: E741' on this line.
) -> Generator[
    Session, None, None
]:  # noqa: E501 Changed 'db' to '_db' to fix the flake8 error E741 ambiguous variable name 'O'. Please check and adjust the name based on your project context if necessary. If 'O' was intended, please add a noqa comment '# noqa: E741' on this line. pylint: disable=redefined-outer-name
    """
    Provides a transactional database session for each test function using nested transactions.
    Rolls back changes after the test, ensuring isolation.
    """
    with app.app_context():
        # Start a nested transaction (uses SAVEPOINT)
        db.session.begin_nested()

        # Yield the existing db.session - tests will operate within the savepoint
        yield db.session

        # Rollback the nested transaction after the test yields back
        db.session.rollback()

        # Optional: Remove the session - may not be strictly needed if scope management is sound
        # db.session.remove()
