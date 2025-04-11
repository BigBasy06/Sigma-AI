# tests/test_routes.py
"""Tests for the main application routes."""

from flask.testing import FlaskClient


def test_index_route(client: FlaskClient):
    """Test the main index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello World from Sigma AI!" in response.data
    assert b"Foundation setup complete." in response.data


def test_health_route(client: FlaskClient):
    """Test the health check route."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"
