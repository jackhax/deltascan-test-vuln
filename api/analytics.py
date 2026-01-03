"""Analytics API endpoints.

Provides endpoints for application analytics, performance
monitoring, and diagnostic information.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import time

from utils.metrics import MetricsCollector, format_metric_name, calculate_percentile
from utils.perf_logger import PerformanceLogger, SystemMonitor

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

# Global instances
_collector = MetricsCollector()
_logger = PerformanceLogger(log_path="/tmp/app_perf.log")
_monitor = SystemMonitor(logger=_logger)


@analytics_bp.route("/record", methods=["POST"])
def record_metric():
    """Record a new metric value.

    Expected JSON body:
    {
        "name": "metric.name",
        "value": 123.45,
        "labels": {"env": "prod"}  // optional
    }
    """
    data = request.get_json() or {}

    name = data.get("name")
    value = data.get("value")
    labels = data.get("labels")

    if not name or value is None:
        return jsonify({"error": "Missing name or value"}), 400

    try:
        value = float(value)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value"}), 400

    _collector.record(name, value, labels)
    _logger.log(name, value, labels)

    return jsonify({"status": "recorded", "metric": name})


@analytics_bp.route("/query", methods=["GET"])
def query_metrics():
    """Query recorded metrics.

    Query params:
    - name: metric name to query
    - summary: if true, return statistical summary
    """
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing metric name"}), 400

    want_summary = request.args.get("summary", "").lower() in ("true", "1", "yes")

    if want_summary:
        return jsonify(_collector.get_summary(name))

    return jsonify({"metrics": _collector.get_metrics(name)})


@analytics_bp.route("/export", methods=["GET"])
def export_metrics():
    """Export all metrics in Prometheus format."""
    content = _collector.export_prometheus()
    return content, 200, {"Content-Type": "text/plain"}


@analytics_bp.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time(),
    })


@analytics_bp.route("/diagnostics", methods=["GET"])
def run_diagnostics():
    """Run system diagnostics.

    Query params:
    - component: system component to diagnose
                 (disk, memory, network, process, or custom)

    Returns diagnostic information for the specified component.
    For built-in components, runs standard system checks.
    For custom components, searches application logs.
    """
    component = request.args.get("component", "disk")

    # Validate component name length to prevent abuse
    if len(component) > 100:
        return jsonify({"error": "Component name too long"}), 400

    # Run diagnostic check
    result = _monitor.run_diagnostic(component)

    return jsonify(result)


@analytics_bp.route("/report", methods=["POST"])
def generate_report():
    """Generate analytics report.

    Expected JSON body:
    {
        "metrics": ["metric1", "metric2"],
        "period": "1h" | "24h" | "7d",
        "format": "json" | "csv"
    }
    """
    data = request.get_json() or {}

    metrics = data.get("metrics", [])
    period = data.get("period", "1h")
    output_format = data.get("format", "json")

    if not metrics:
        return jsonify({"error": "No metrics specified"}), 400

    # Build report
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "period": period,
        "metrics": {},
    }

    for metric_name in metrics:
        summary = _collector.get_summary(metric_name)
        report["metrics"][metric_name] = summary

    if output_format == "csv":
        # Simple CSV output
        lines = ["metric,count,avg,min,max"]
        for name, stats in report["metrics"].items():
            lines.append(f"{name},{stats['count']},{stats['avg']},{stats['min']},{stats['max']}")
        return "\n".join(lines), 200, {"Content-Type": "text/csv"}

    return jsonify(report)


@analytics_bp.route("/benchmark", methods=["POST"])
def run_benchmark():
    """Run performance benchmark.

    Executes a series of operations and measures performance.
    Used for capacity planning and performance regression testing.
    """
    data = request.get_json() or {}

    iterations = min(data.get("iterations", 1000), 10000)
    operation = data.get("operation", "hash")

    start_time = time.time()

    if operation == "hash":
        import hashlib
        for i in range(iterations):
            hashlib.sha256(f"test{i}".encode()).hexdigest()
    elif operation == "json":
        import json
        for i in range(iterations):
            json.dumps({"key": f"value{i}", "nested": {"a": 1}})
    elif operation == "sleep":
        time.sleep(min(iterations / 1000, 5))

    elapsed = time.time() - start_time

    _collector.record(f"benchmark.{operation}", elapsed, {"iterations": iterations})

    return jsonify({
        "operation": operation,
        "iterations": iterations,
        "elapsed_seconds": elapsed,
        "ops_per_second": iterations / elapsed if elapsed > 0 else 0,
    })
