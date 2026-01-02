"""Webhook API endpoints."""

import requests
from flask import Blueprint, request, jsonify
from utils.validators import validate_webhook_url

webhooks_bp = Blueprint("webhooks", __name__)

registered_webhooks = {}


@webhooks_bp.route("/api/webhooks", methods=["POST"])
def register_webhook():
    """Register a new webhook."""
    data = request.get_json()
    url = data.get("url", "")
    name = data.get("name", "")
    
    if not validate_webhook_url(url):
        return jsonify({"error": "Invalid webhook URL"}), 400
    
    webhook_id = len(registered_webhooks) + 1
    registered_webhooks[webhook_id] = {"name": name, "url": url}
    
    return jsonify({"id": webhook_id, "message": "Webhook registered"})


@webhooks_bp.route("/api/webhooks/<int:webhook_id>/test", methods=["POST"])
def test_webhook(webhook_id):
    """Test a webhook by sending a request."""
    webhook = registered_webhooks.get(webhook_id)
    if not webhook:
        return jsonify({"error": "Webhook not found"}), 404
    
    try:
        response = requests.post(
            webhook["url"],
            json={"test": True, "webhook_id": webhook_id},
            timeout=10
        )
        return jsonify({
            "status": response.status_code,
            "body": response.text[:500]
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/api/fetch", methods=["POST"])
def fetch_url():
    """Fetch content from URL."""
    data = request.get_json()
    url = data.get("url", "")
    
    if not url.startswith("http"):
        return jsonify({"error": "Invalid URL scheme"}), 400
    
    response = requests.get(url, timeout=10)
    return jsonify({
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "body": response.text[:1000]
    })

