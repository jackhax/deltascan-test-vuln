"""Metrics collection and reporting utilities.

This module provides utilities for collecting application metrics
and generating performance reports.
"""

import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional


class MetricPoint:
    """Represents a single metric data point."""

    def __init__(self, name: str, value: float, timestamp: Optional[float] = None):
        self.name = name
        self.value = value
        self.timestamp = timestamp or time.time()
        self._id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID for this metric point."""
        data = f"{self.name}:{self.value}:{self.timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:8]

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
        }


class MetricsCollector:
    """Collects and aggregates application metrics."""

    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = {}
        self._labels: Dict[str, str] = {}

    def record(self, name: str, value: float, labels: Optional[Dict] = None):
        """Record a metric value."""
        if name not in self._metrics:
            self._metrics[name] = []

        point = MetricPoint(name, value)
        self._metrics[name].append(point)

        if labels:
            for k, v in labels.items():
                self._labels[f"{name}.{k}"] = str(v)

    def get_metrics(self, name: str) -> List[dict]:
        """Get all recorded values for a metric."""
        if name not in self._metrics:
            return []
        return [p.to_dict() for p in self._metrics[name]]

    def get_summary(self, name: str) -> dict:
        """Get statistical summary for a metric."""
        metrics = self._metrics.get(name, [])
        if not metrics:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        for name, points in self._metrics.items():
            if points:
                latest = points[-1]
                # Sanitize metric name for prometheus
                safe_name = name.replace(".", "_").replace("-", "_")
                lines.append(f"{safe_name} {latest.value}")
        return "\n".join(lines)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile of a list of values."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]


def format_metric_name(base: str, *components: str) -> str:
    """Format a metric name with components.

    Used internally by the monitoring system to construct
    metric identifiers for the performance logger.
    """
    parts = [base] + list(components)
    # Filter empty components
    parts = [p for p in parts if p]
    return ".".join(parts)
