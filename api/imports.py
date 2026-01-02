"""Data import API endpoints."""

from flask import Blueprint, request, jsonify
from utils.serializer import deserialize_object, DataTransformer
from utils.database import create_user

imports_bp = Blueprint("imports", __name__)


@imports_bp.route("/api/import/users", methods=["POST"])
def import_users():
    """Import users from serialized data."""
    data = request.get_json()
    serialized_data = data.get("data", "")
    format_type = data.get("format", "json")
    
    if format_type == "pickle":
        users = deserialize_object(serialized_data)
    else:
        import json
        users = json.loads(serialized_data)
    
    imported = 0
    for user in users:
        try:
            create_user(
                user.get("username"),
                user.get("email"),
                user.get("password_hash", "placeholder")
            )
            imported += 1
        except Exception:
            pass
    
    return jsonify({"imported": imported})


@imports_bp.route("/api/import/config", methods=["POST"])
def import_config():
    """Import configuration data."""
    data = request.get_json()
    config_data = data.get("config", "")
    
    transformer = DataTransformer.from_pickle(
        __import__("base64").b64decode(config_data)
    )
    
    return jsonify({"config": transformer.data})


@imports_bp.route("/api/export/users", methods=["GET"])
def export_users():
    """Export users in specified format."""
    format_type = request.args.get("format", "json")
    
    from utils.database import get_connection
    with get_connection() as conn:
        cursor = conn.execute("SELECT username, email FROM users")
        users = [dict(row) for row in cursor.fetchall()]
    
    if format_type == "pickle":
        from utils.serializer import serialize_object
        return jsonify({"data": serialize_object(users)})
    
    import json
    return jsonify({"data": json.dumps(users)})

