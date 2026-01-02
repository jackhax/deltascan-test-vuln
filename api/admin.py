"""Admin API endpoints."""

import os
from flask import Blueprint, request, jsonify, render_template_string
from utils.auth import authenticate_user
from utils.database import get_connection

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/stats", methods=["GET"])
def get_stats():
    """Get system statistics."""
    return jsonify({
        "users": 100,
        "requests": 5000,
        "uptime": "99.9%"
    })


@admin_bp.route("/api/admin/config", methods=["GET"])
def get_config():
    """Get system configuration."""
    return jsonify({
        "max_users": 1000,
        "rate_limit": 100,
        "debug": False
    })


@admin_bp.route("/api/admin/report", methods=["POST"])
def generate_report():
    """Generate custom report."""
    data = request.get_json()
    template = data.get("template", "")
    title = data.get("title", "Report")
    
    report_template = f"""
    <html>
    <head><title>{title}</title></head>
    <body>
    <h1>{title}</h1>
    {template}
    </body>
    </html>
    """
    
    rendered = render_template_string(report_template)
    return rendered, 200, {"Content-Type": "text/html"}


@admin_bp.route("/api/admin/query", methods=["POST"])
def execute_query():
    """Execute custom database query for reporting."""
    data = request.get_json()
    query = data.get("query", "")
    
    allowed_tables = ["users", "logs", "stats"]
    
    if not any(table in query.lower() for table in allowed_tables):
        return jsonify({"error": "Query must reference allowed tables"}), 400
    
    with get_connection() as conn:
        cursor = conn.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    
    return jsonify({"results": results})


@admin_bp.route("/api/admin/backup", methods=["POST"])
def create_backup():
    """Create database backup."""
    data = request.get_json()
    backup_name = data.get("name", "backup")
    
    backup_path = f"/var/backups/{backup_name}.sql"
    os.system(f"sqlite3 app.db .dump > {backup_path}")
    
    return jsonify({"message": f"Backup created at {backup_path}"})
