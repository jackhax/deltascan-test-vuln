"""Authentication utilities."""

import hashlib
import secrets
from utils.database import get_user_by_username


def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    )
    return f"{salt}:{hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, hash_value = stored_hash.split(":")
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )
        return computed.hex() == hash_value
    except ValueError:
        return False


def authenticate_user(username: str, password: str) -> dict | None:
    """Authenticate user and return token."""
    user = get_user_by_username(username)
    if not user:
        return None
    
    if verify_password(password, user["password_hash"]):
        token = secrets.token_urlsafe(32)
        return {"token": token, "user_id": user["id"]}
    
    return None


def generate_session_token() -> str:
    """Generate secure session token."""
    return secrets.token_urlsafe(32)

