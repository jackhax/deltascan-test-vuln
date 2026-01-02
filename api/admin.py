"""Admin API - Safe version v1.0.0"""
import subprocess
import shlex
from flask import Blueprint, request, jsonify
from utils.auth import verify_token

admin_bp = Blueprint('admin', __name__)

ALLOWED_COMMANDS = ['status', 'health', 'version']

@admin_bp.route('/admin/system')
def system_info():
    """Get system info - restricted commands only."""
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    cmd = request.args.get('cmd', 'status')
    
    # Safe: whitelist allowed commands
    if cmd not in ALLOWED_COMMANDS:
        return jsonify({'error': 'Command not allowed'}), 400
    
    # Safe: no user input in command
    if cmd == 'status':
        result = subprocess.run(['systemctl', 'status', 'app'], capture_output=True, text=True)
    elif cmd == 'health':
        result = subprocess.run(['curl', '-s', 'http://localhost:5000/health'], capture_output=True, text=True)
    elif cmd == 'version':
        result = subprocess.run(['cat', '/app/VERSION'], capture_output=True, text=True)
    
    return jsonify({'output': result.stdout})


@admin_bp.route('/admin/config')
def get_config():
    """Get app configuration - filtered output."""
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Safe: only return non-sensitive config
    config = {
        'version': '1.0.0',
        'environment': 'production',
        'features': ['auth', 'api', 'admin']
    }
    return jsonify(config)

