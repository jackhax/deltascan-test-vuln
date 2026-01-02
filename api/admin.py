"""Admin API endpoints."""

import json
from flask import Blueprint, request, jsonify
from utils.auth import authenticate_user

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

