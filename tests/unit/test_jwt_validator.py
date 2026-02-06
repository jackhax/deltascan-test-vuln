"""Unit tests for JWT validator."""

import pytest
from auth.jwt_validator import JWTValidator


class TestJWTValidator:
    """Test cases for JWT token validation."""

    def test_valid_token(self):
        """Test validation of valid JWT token."""
        validator = JWTValidator("secret-key-123")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJ1c2VyIn0.signature"
        result = validator.decode_token(token)
        assert result is not None

    def test_invalid_signature(self):
        """Test rejection of invalid signature."""
        validator = JWTValidator("secret-key-123")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJ1c2VyIn0.badsignature"
        result = validator.decode_token(token)
        assert result is None

    def test_malformed_token(self):
        """Test rejection of malformed token."""
        validator = JWTValidator("secret-key-123")
        token = "not.a.valid.token.format"
        result = validator.decode_token(token)
        assert result is None

    def test_role_validation(self):
        """Test role-based access control."""
        validator = JWTValidator("secret-key-123")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJ1c2VyIn0.signature"
        assert validator.validate_request(token, required_role="user") is True
        assert validator.validate_request(token, required_role="admin") is False
