"""Authentication utilities - Safe version v1.0.0"""
import os
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('SECRET_KEY')

def verify_token(token: str) -> bool:
    """Verify JWT token - secure implementation."""
    if not token or not SECRET_KEY:
        return False
    
    try:
        # Secure token verification
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{parts[0]}.{parts[1]}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_sig, parts[2])
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash password with salt - secure."""
    salt = secrets.token_hex(32)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000  # Strong iteration count
    )
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, hash_value = stored_hash.split('$')
        expected = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return hmac.compare_digest(expected.hex(), hash_value)
    except Exception:
        return False

