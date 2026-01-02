"""Main application - Version v1.1.0 with vulnerabilities for testing"""
import os
from flask import Flask, request, jsonify
from utils.database import get_db_connection, execute_raw_query
from utils.auth import verify_token

app = Flask(__name__)

@app.route('/api/users/<int:user_id>')
def get_user(user_id: int):
    """Get user by ID."""
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'id': user[0], 'name': user[1], 'email': user[2]})
    return jsonify({'error': 'User not found'}), 404


@app.route('/api/users/search')
def search_users():
    """Search users - VULNERABLE: SQL Injection."""
    name = request.args.get('name', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection - user input directly in query
    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return jsonify({'users': users})


@app.route('/api/search')
def search():
    """Search endpoint - VULNERABLE: XSS."""
    query = request.args.get('q', '')
    # VULNERABLE: No sanitization - XSS vulnerability
    return jsonify({'query': query, 'results': [], 'message': f'Results for: {query}'})


@app.route('/api/file')
def get_file():
    """Get file content - VULNERABLE: Path Traversal."""
    filename = request.args.get('name', '')
    # VULNERABLE: Path traversal - no validation on filename
    filepath = f'/app/data/{filename}'
    
    try:
        with open(filepath, 'r') as f:
            return jsonify({'content': f.read()})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/render')
def render_template():
    """Render template - VULNERABLE: SSTI."""
    from jinja2 import Template
    user_template = request.args.get('template', 'Hello {{ name }}')
    name = request.args.get('name', 'World')
    # VULNERABLE: Server-side template injection
    t = Template(user_template)
    return t.render(name=name)


@app.route('/api/execute')
def execute_code():
    """Execute code - VULNERABLE: Code Injection."""
    code = request.args.get('code', '1+1')
    # VULNERABLE: Arbitrary code execution via eval
    try:
        result = eval(code)
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/redirect')
def redirect_url():
    """Redirect to URL - VULNERABLE: Open Redirect."""
    url = request.args.get('url', '/')
    # VULNERABLE: Open redirect - no validation
    from flask import redirect
    return redirect(url)


@app.route('/api/debug')
def debug_info():
    """Debug endpoint - VULNERABLE: Information Disclosure."""
    # VULNERABLE: Exposes sensitive information
    return jsonify({
        'env': dict(os.environ),
        'config': {
            'db_password': os.environ.get('DB_PASSWORD'),
            'secret_key': os.environ.get('SECRET_KEY'),
            'api_keys': os.environ.get('API_KEYS')
        }
    })


if __name__ == '__main__':
    # VULNERABLE: Debug mode enabled, binding to all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
