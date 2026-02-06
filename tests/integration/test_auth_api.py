"""Integration tests for authentication API."""

import pytest
import requests


class TestAuthAPI:
    """Test authentication endpoints."""

    def test_login_endpoint(self):
        """Test user login."""
        response = requests.post("http://localhost:8000/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        assert "token" in response.json()

    def test_protected_endpoint(self):
        """Test accessing protected endpoint with valid token."""
        token = "valid.jwt.token"
        response = requests.get(
            "http://localhost:8000/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
