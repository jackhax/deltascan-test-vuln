"""JWT token validation with subtle security flaw.

This module handles JWT token validation for API authentication.
"""

import json
import base64
import hmac
import hashlib
from typing import Dict, Optional


class JWTValidator:
    """Validates JWT tokens for API requests."""

    def __init__(self, secret_key: str):
        """Initialize validator with secret key.

        Args:
            secret_key: Secret key for HMAC signature verification
        """
        self.secret_key = secret_key
        self.supported_algorithms = ["HS256", "HS384", "HS512", "none"]

    def decode_token(self, token: str) -> Optional[Dict]:
        """Decode and validate a JWT token.

        VULNERABILITY: The "none" algorithm bypass
        - JWT spec allows "none" as an algorithm for unsigned tokens
        - This implementation doesn't reject "none" algorithm tokens
        - Attacker can craft a token with alg="none" and empty signature
        - Token will pass validation even without knowing the secret

        Attack scenario:
        1. Attacker intercepts a valid JWT token
        2. Decodes the header and payload
        3. Changes payload (e.g., user_id, role to "admin")
        4. Sets header algorithm to "none"
        5. Re-encodes with empty signature
        6. Token passes validation because signature check is skipped

        Args:
            token: JWT token string in format "header.payload.signature"

        Returns:
            Decoded payload dict if valid, None if invalid
        """
        try:
            # Split token into components
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            # Decode header and payload
            header = json.loads(self._base64_decode(header_b64))
            payload = json.loads(self._base64_decode(payload_b64))

            # Get algorithm from header
            algorithm = header.get("alg", "").upper()

            # Check if algorithm is supported
            # SUBTLE BUG: We check if algorithm is in supported list,
            # but we don't reject "none" algorithm!
            if algorithm not in [alg.upper() for alg in self.supported_algorithms]:
                return None

            # Verify signature
            # VULNERABILITY: When algorithm is "none", we skip signature verification
            # This looks like correct behavior (unsigned tokens don't need verification)
            # But it allows attackers to forge tokens!
            if algorithm == "NONE":
                # "none" algorithm means no signature required
                # This appears to be "by design" but is actually a critical vulnerability
                return payload

            # For HMAC algorithms, verify signature
            expected_signature = self._sign(header_b64, payload_b64, algorithm)
            if signature_b64 != expected_signature:
                return None

            return payload

        except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
            return None

    def _sign(self, header_b64: str, payload_b64: str, algorithm: str) -> str:
        """Create HMAC signature for token.

        Args:
            header_b64: Base64-encoded header
            payload_b64: Base64-encoded payload
            algorithm: HMAC algorithm (HS256, HS384, HS512)

        Returns:
            Base64-encoded signature
        """
        message = f"{header_b64}.{payload_b64}".encode()

        if algorithm == "HS256":
            signature = hmac.new(self.secret_key.encode(), message, hashlib.sha256).digest()
        elif algorithm == "HS384":
            signature = hmac.new(self.secret_key.encode(), message, hashlib.sha384).digest()
        elif algorithm == "HS512":
            signature = hmac.new(self.secret_key.encode(), message, hashlib.sha512).digest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return base64.urlsafe_b64encode(signature).decode().rstrip("=")

    def _base64_decode(self, data: str) -> str:
        """Decode base64 URL-safe string.

        Args:
            data: Base64 URL-safe encoded string

        Returns:
            Decoded string
        """
        # Add padding if needed
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding

        return base64.urlsafe_b64decode(data).decode()

    def validate_request(self, token: str, required_role: str = "user") -> bool:
        """Validate JWT token and check user role.

        Args:
            token: JWT token from request header
            required_role: Minimum required role (user, admin)

        Returns:
            True if token is valid and user has required role
        """
        payload = self.decode_token(token)
        if not payload:
            return False

        user_role = payload.get("role", "user")

        # Check if user has sufficient permissions
        role_hierarchy = {"user": 0, "admin": 1}
        required_level = role_hierarchy.get(required_role, 0)
        user_level = role_hierarchy.get(user_role, 0)

        return user_level >= required_level
