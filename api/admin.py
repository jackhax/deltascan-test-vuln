"""Admin API - Version v1.2.0"""
import subprocess
import os
import pickle
from flask import Blueprint, request, jsonify
from utils.auth import verify_token, check_admin

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/system')
def system_info():
    """Get system info."""
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    cmd = request.args.get('cmd', 'whoami')
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({'output': result.stdout, 'error': result.stderr})


@admin_bp.route('/admin/exec', methods=['POST'])
def execute_system():
    """Execute system command."""
    data = request.get_json()
    command = data.get('command', '')
    args = data.get('args', [])
    
    result = subprocess.run([command] + args, capture_output=True, text=True)
    return jsonify({'stdout': result.stdout, 'stderr': result.stderr})


@admin_bp.route('/admin/config')
def get_config():
    """Get app configuration."""
    return jsonify({
        'env': dict(os.environ),
        'version': '1.2.0',
        'debug': True
    })


@admin_bp.route('/admin/deserialize', methods=['POST'])
def deserialize_data():
    """Deserialize data."""
    import base64
    data = request.get_json()
    serialized = data.get('data', '')
    
    try:
        decoded = base64.b64decode(serialized)
        obj = pickle.loads(decoded)
        return jsonify({'result': str(obj)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/admin/upload', methods=['POST'])
def upload_file():
    """Upload file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    filename = file.filename
    
    upload_path = f'/app/uploads/{filename}'
    file.save(upload_path)
    
    return jsonify({'path': upload_path})


@admin_bp.route('/admin/log')
def read_log():
    """Read log file."""
    log_file = request.args.get('file', 'app.log')
    log_path = f'/var/log/{log_file}'
    
    try:
        with open(log_path, 'r') as f:
            return jsonify({'content': f.read()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/admin/proxy')
def proxy_request():
    """Proxy request."""
    import requests
    url = request.args.get('url', '')
    
    try:
        resp = requests.get(url, timeout=5)
        return jsonify({'status': resp.status_code, 'body': resp.text[:1000]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/admin/xml', methods=['POST'])
def parse_xml():
    """Parse XML."""
    from lxml import etree
    xml_data = request.data
    
    parser = etree.XMLParser(resolve_entities=True, no_network=False)
    try:
        doc = etree.fromstring(xml_data, parser)
        return jsonify({'root': doc.tag, 'text': doc.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
