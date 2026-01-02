"""Database utilities - Safe version v1.0.0"""
import os
import psycopg2

def get_db_connection():
    """Get database connection with secure defaults."""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME', 'app'),
        user=os.environ.get('DB_USER', 'app'),
        password=os.environ.get('DB_PASSWORD'),
        sslmode='require'  # Safe: require SSL
    )


def execute_query(query: str, params: tuple = None):
    """Execute a query with parameters (safe)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

