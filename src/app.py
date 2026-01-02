"""Main application - Safe version v1.0.0"""
import os
from flask import Flask, request, jsonify
from utils.database import get_db_connection
from utils.auth import verify_token

app = Flask(__name__)

@app.route('/api/users/<int:user_id>')
def get_user(user_id: int):
    """Get user by ID - uses parameterized query (safe)."""
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Safe: parameterized query
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'id': user[0], 'name': user[1], 'email': user[2]})
    return jsonify({'error': 'User not found'}), 404


@app.route('/api/search')
def search():
    """Search endpoint - properly sanitized."""
    query = request.args.get('q', '')
    # Safe: input sanitization
    sanitized_query = query.replace('<', '&lt;').replace('>', '&gt;')
    
    return jsonify({'query': sanitized_query, 'results': []})


@app.route('/api/file')
def get_file():
    """Get file content - with path validation."""
    filename = request.args.get('name', '')
    # Safe: restrict to allowed directory
    allowed_dir = '/app/public/'
    filepath = os.path.join(allowed_dir, os.path.basename(filename))
    
    if not filepath.startswith(allowed_dir):
        return jsonify({'error': 'Invalid path'}), 400
    
    try:
        with open(filepath, 'r') as f:
            return jsonify({'content': f.read()})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

