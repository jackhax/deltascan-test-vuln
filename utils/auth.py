"""Authentication utilities - Version v1.1.0 with vulnerabilities"""
import os
import hashlib
import base64

# VULNERABLE: Hardcoded secret key
SECRET_KEY = "my_super_secret_key_12345"

def verify_token(token: str) -> bool:
    """Verify token - VULNERABLE: Weak verification."""
    if not token:
        return False
    
    try:
        # VULNERABLE: Simple base64 decode, no signature verification
        decoded = base64.b64decode(token)
        parts = decoded.decode().split(':')
        # VULNERABLE: No expiration check, no signature
        return len(parts) == 2 and parts[0].isdigit()
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash password - VULNERABLE: Weak hashing."""
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password - VULNERABLE: Timing attack."""
    hashed = hash_password(password)
    # VULNERABLE: Non-constant time comparison
    return hashed == stored_hash


def generate_reset_token(user_id: int) -> str:
    """Generate password reset token - VULNERABLE: Predictable."""
    import time
    # VULNERABLE: Predictable token based on time and user_id
    timestamp = int(time.time())
    token = f"{user_id}:{timestamp}"
    return base64.b64encode(token.encode()).decode()


def create_session(user_id: int) -> str:
    """Create session - VULNERABLE: Weak session token."""
    # VULNERABLE: Sequential/predictable session ID
    return f"session_{user_id}_{hash_password(str(user_id))[:8]}"


# VULNERABLE: Hardcoded admin credentials for testing
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def check_admin(username: str, password: str) -> bool:
    """Check admin credentials - VULNERABLE: Hardcoded creds."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
