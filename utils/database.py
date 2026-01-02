"""Database utilities."""

import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "app.db"


@contextmanager
def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database schema."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def get_user_by_id(user_id: int) -> dict | None:
    """Get user by ID using parameterized query."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_username(username: str) -> dict | None:
    """Get user by username using parameterized query."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def create_user(username: str, email: str, password_hash: str) -> dict:
    """Create new user using parameterized query."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return {"id": cursor.lastrowid, "username": username, "email": email}

