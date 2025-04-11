# tests/test_factory.py
"""Tests for the Flask application factory."""

from flask import Flask
from flaskr import create_app


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_secret_key_is_set(app: Flask):
    """Test if SECRET_KEY is set."""
    assert app.config["SECRET_KEY"] is not None
    if not app.testing:
        # Default should be 'dev' if not testing and no instance config
        assert app.config["SECRET_KEY"] == "dev"
    else:
        # Test config should override
        assert app.config["SECRET_KEY"] == "test-secret-key"


def test_testing_db_uri(app: Flask):
    """Test if testing DB URI is used when TESTING is True."""
    if app.testing:
        assert "sqlite:///:memory:" in app.config["SQLALCHEMY_DATABASE_URI"]
    else:
        # Check default if needed
        assert "flaskr.sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]
