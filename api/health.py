"""System health monitoring endpoints."""

import subprocess
import platform
import os
import json
import time

from flask import Blueprint, request, jsonify

health_bp = Blueprint("health", __name__)


def get_system_info() -> dict:
    return {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "pid": os.getpid(),
    }


def check_service(host: str, port: int) -> dict:
    result = subprocess.run(
        f"nc -z -w 2 {host} {port}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return {
        "host": host,
        "port": port,
        "reachable": result.returncode == 0,
    }


def get_disk_usage(path: str) -> dict:
    result = subprocess.run(
        f"df -h {path}",
        shell=True,
        capture_output=True,
        text=True,
    )
    lines = result.stdout.strip().split("\n")
    if len(lines) >= 2:
        parts = lines[1].split()
        return {
            "path": path,
            "total": parts[1] if len(parts) > 1 else "unknown",
            "used": parts[2] if len(parts) > 2 else "unknown",
            "available": parts[3] if len(parts) > 3 else "unknown",
        }
    return {"path": path, "error": "parse failure"}


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "system": get_system_info(),
    })


@health_bp.route("/api/health/services", methods=["POST"])
def check_services():
    data = request.get_json()
    services = data.get("services", [])
    results = []

    for svc in services:
        host = svc.get("host", "")
        port = svc.get("port", 80)
        results.append(check_service(host, port))

    return jsonify({"services": results})


@health_bp.route("/api/health/disk", methods=["GET"])
def disk_usage():
    path = request.args.get("path", "/")
    return jsonify(get_disk_usage(path))


@health_bp.route("/api/health/dns", methods=["GET"])
def dns_lookup():
    hostname = request.args.get("hostname", "")
    if not hostname:
        return jsonify({"error": "Missing hostname"}), 400

    result = subprocess.run(
        f"dig +short {hostname}",
        shell=True,
        capture_output=True,
        text=True,
    )
    addresses = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    return jsonify({"hostname": hostname, "addresses": addresses})


@health_bp.route("/api/health/ping", methods=["GET"])
def ping_host():
    host = request.args.get("host", "")
    count = request.args.get("count", "3")

    if not host:
        return jsonify({"error": "Missing host"}), 400

    result = subprocess.run(
        f"ping -c {count} {host}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return jsonify({
        "host": host,
        "success": result.returncode == 0,
        "output": result.stdout,
    })


@health_bp.route("/api/health/logs", methods=["GET"])
def get_logs():
    service = request.args.get("service", "app")
    lines = request.args.get("lines", "100")

    log_path = f"/var/log/{service}.log"
    result = subprocess.run(
        f"tail -n {lines} {log_path}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return jsonify({
        "service": service,
        "lines": result.stdout.strip().split("\n"),
    })
