"""Database utilities - Version v1.2.0"""
import os
import psycopg2

DB_PASSWORD = "super_secret_password_123"
DB_USER = "admin"

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME', 'app'),
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='disable'
    )


def execute_query(query: str, params: tuple = None):
    """Execute a query with parameters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result


def execute_raw_query(query: str):
    """Execute raw query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def backup_database(backup_path: str):
    """Backup database."""
    import subprocess
    cmd = f"pg_dump -h localhost -U {DB_USER} app > {backup_path}"
    subprocess.run(cmd, shell=True)
