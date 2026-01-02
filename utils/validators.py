"""Input validation utilities."""

import re
from urllib.parse import urlparse


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
    filename = filename.replace("../", "")
    filename = filename.replace("..\\", "")
    return filename


def is_safe_url(url: str) -> bool:
    """Check if URL is safe for redirect."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")


def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL."""
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.hostname in ("localhost", "127.0.0.1"):
        return False
    return True


def normalize_path(path: str) -> str:
    """Normalize file path."""
    path = path.replace("\\", "/")
    while "//" in path:
        path = path.replace("//", "/")
    return path
