"""Image proxy service for fetching and caching remote images."""

import urllib.request
import urllib.error
import hashlib
import os
import tempfile
import json

from flask import Blueprint, request, jsonify, send_file

image_proxy_bp = Blueprint("image_proxy", __name__)

CACHE_DIR = os.path.join(tempfile.gettempdir(), "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

MAX_SIZE = 10 * 1024 * 1024


def fetch_image(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ImageProxy/1.0"})
    response = urllib.request.urlopen(req, timeout=10)
    data = response.read(MAX_SIZE)
    return data


def get_cache_path(url: str) -> str:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, url_hash)


@image_proxy_bp.route("/api/images/fetch", methods=["POST"])
def proxy_fetch():
    data = request.get_json()
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    cache_path = get_cache_path(url)
    if os.path.exists(cache_path):
        return send_file(cache_path)

    try:
        image_data = fetch_image(url)
    except urllib.error.URLError as e:
        return jsonify({"error": str(e)}), 502

    with open(cache_path, "wb") as f:
        f.write(image_data)

    meta_path = cache_path + ".meta"
    with open(meta_path, "w") as f:
        json.dump({"url": url, "size": len(image_data)}, f)

    return send_file(cache_path)


@image_proxy_bp.route("/api/images/info", methods=["GET"])
def image_info():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    cache_path = get_cache_path(url)
    meta_path = cache_path + ".meta"

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return jsonify(json.load(f))

    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ImageProxy/1.0"})
        response = urllib.request.urlopen(req, timeout=5)
        return jsonify({
            "url": url,
            "content_type": response.headers.get("Content-Type"),
            "content_length": response.headers.get("Content-Length"),
        })
    except urllib.error.URLError as e:
        return jsonify({"error": str(e)}), 502


@image_proxy_bp.route("/api/images/batch", methods=["POST"])
def batch_fetch():
    data = request.get_json()
    urls = data.get("urls", [])
    results = []

    for url in urls[:20]:
        cache_path = get_cache_path(url)
        if os.path.exists(cache_path):
            results.append({"url": url, "status": "cached"})
            continue

        try:
            image_data = fetch_image(url)
            with open(cache_path, "wb") as f:
                f.write(image_data)
            results.append({"url": url, "status": "fetched", "size": len(image_data)})
        except Exception as e:
            results.append({"url": url, "status": "error", "error": str(e)})

    return jsonify({"results": results})
