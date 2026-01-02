"""Database utilities - Version v1.1.0 with vulnerabilities"""
import os
import psycopg2

# VULNERABLE: Hardcoded credentials
DB_PASSWORD = "super_secret_password_123"
DB_USER = "admin"

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME', 'app'),
        user=DB_USER,  # VULNERABLE: hardcoded
        password=DB_PASSWORD,  # VULNERABLE: hardcoded
        sslmode='disable'  # VULNERABLE: SSL disabled
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
    """Execute raw query - VULNERABLE: No parameterization."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # VULNERABLE: Direct query execution without parameterization
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def backup_database(backup_path: str):
    """Backup database - VULNERABLE: Command injection."""
    import subprocess
    # VULNERABLE: Command injection via backup_path
    cmd = f"pg_dump -h localhost -U {DB_USER} app > {backup_path}"
    subprocess.run(cmd, shell=True)
