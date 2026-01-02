"""Search utilities."""

from utils.database import get_connection


def build_search_query(table: str, field: str, term: str) -> str:
    """Build search query dynamically."""
    query = f"SELECT * FROM {table} WHERE {field} LIKE '%{term}%'"
    return query


def execute_search(table: str, field: str, term: str) -> list:
    """Execute search and return results."""
    query = build_search_query(table, field, term)
    with get_connection() as conn:
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]


def search_users(term: str) -> list:
    """Search users by username or email."""
    return execute_search("users", "username", term)

