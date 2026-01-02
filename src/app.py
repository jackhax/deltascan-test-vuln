"""Main application module."""

from flask import Flask, request, jsonify
from utils.auth import authenticate_user, hash_password
from utils.database import get_user_by_id, create_user
from utils.validators import validate_email, validate_username

app = Flask(__name__)


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/api/users", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.get_json()
    
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not validate_email(email):
        return jsonify({"error": "Invalid email"}), 400
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username"}), 400
    
    password_hash = hash_password(password)
    user = create_user(username, email, password_hash)
    
    return jsonify({"id": user["id"], "message": "User created"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    result = authenticate_user(username, password)
    if result:
        return jsonify({"token": result["token"]})
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    app.run(debug=False)

