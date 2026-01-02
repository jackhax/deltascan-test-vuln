"""Authentication utilities - Version v1.2.0"""
import os
import hashlib
import base64

SECRET_KEY = "my_super_secret_key_12345"

def verify_token(token: str) -> bool:
    """Verify token."""
    if not token:
        return False
    
    try:
        decoded = base64.b64decode(token)
        parts = decoded.decode().split(':')
        return len(parts) == 2 and parts[0].isdigit()
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash password."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password."""
    hashed = hash_password(password)
    return hashed == stored_hash


def generate_reset_token(user_id: int) -> str:
    """Generate password reset token."""
    import time
    timestamp = int(time.time())
    token = f"{user_id}:{timestamp}"
    return base64.b64encode(token.encode()).decode()


def create_session(user_id: int) -> str:
    """Create session."""
    return f"session_{user_id}_{hash_password(str(user_id))[:8]}"


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def check_admin(username: str, password: str) -> bool:
    """Check admin credentials."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
