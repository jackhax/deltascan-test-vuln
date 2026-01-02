"""Input validation utilities."""

import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 254:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format."""
    if not username or len(username) < 3 or len(username) > 30:
        return False
    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, username))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")
    return filename


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r"^https?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._/-]*)?$"
    return bool(re.match(pattern, url))

