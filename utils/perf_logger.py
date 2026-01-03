"""Performance logging utilities.

Provides async-safe logging for performance metrics with
support for file rotation and external log aggregation.
"""

import os
import time
import threading
import subprocess
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path


class LogRotator:
    """Handles log file rotation."""

    def __init__(self, base_path: str, max_size: int = 10_000_000):
        self.base_path = Path(base_path)
        self.max_size = max_size
        self._lock = threading.Lock()

    def should_rotate(self) -> bool:
        if not self.base_path.exists():
            return False
        return self.base_path.stat().st_size > self.max_size

    def rotate(self):
        with self._lock:
            if self.base_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = self.base_path.with_suffix(f".{timestamp}.log")
                self.base_path.rename(new_path)


class PerformanceLogger:
    """Logs performance metrics to file and external systems."""

    def __init__(
        self,
        log_path: str = "/var/log/app/performance.log",
        external_endpoint: Optional[str] = None,
    ):
        self.log_path = Path(log_path)
        self.external_endpoint = external_endpoint
        self._rotator = LogRotator(log_path)
        self._buffer = []
        self._flush_interval = 5.0
        self._last_flush = time.time()

    def log(self, metric_name: str, value: float, tags: Optional[dict] = None):
        """Log a performance metric."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "metric": metric_name,
            "value": value,
            "tags": tags or {},
        }
        self._buffer.append(entry)

        if time.time() - self._last_flush > self._flush_interval:
            self._flush()

    def _flush(self):
        """Flush buffered entries to disk."""
        if not self._buffer:
            return

        self._last_flush = time.time()

        # Ensure directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Check rotation
        if self._rotator.should_rotate():
            self._rotator.rotate()

        # Write entries
        with open(self.log_path, "a") as f:
            for entry in self._buffer:
                line = f"{entry['timestamp']} {entry['metric']}={entry['value']}"
                if entry["tags"]:
                    tags_str = ",".join(f"{k}={v}" for k, v in entry["tags"].items())
                    line += f" {tags_str}"
                f.write(line + "\n")

        self._buffer = []

    def export_to_graphite(self, host: str, port: int = 2003):
        """Export metrics to Graphite."""
        # Implementation placeholder
        pass


class SystemMonitor:
    """Monitors system performance metrics."""

    def __init__(self, logger: Optional[PerformanceLogger] = None):
        self.logger = logger
        self._running = False
        self._thread = None

    def start(self):
        """Start background monitoring."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop background monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _monitor_loop(self):
        while self._running:
            self._collect_metrics()
            time.sleep(10)

    def _collect_metrics(self):
        """Collect system metrics."""
        # CPU usage via /proc/stat parsing
        # Memory via /proc/meminfo
        pass

    def run_diagnostic(self, component: str) -> dict:
        """Run diagnostic check on a specific component.

        Executes system checks and returns diagnostic information.
        The component parameter specifies which subsystem to check.
        """
        results = {"component": component, "timestamp": time.time()}

        # Run component-specific checks
        check_commands = {
            "disk": "df -h",
            "memory": "free -m",
            "network": "netstat -s",
            "process": "ps aux",
        }

        if component in check_commands:
            cmd = check_commands[component]
            try:
                output = subprocess.check_output(cmd.split(), timeout=30)
                results["output"] = output.decode("utf-8", errors="ignore")
                results["status"] = "ok"
            except subprocess.TimeoutExpired:
                results["status"] = "timeout"
            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)
        else:
            # For custom components, use the provided name in the check
            results.update(self._run_custom_check(component))

        return results

    def _run_custom_check(self, component_name: str) -> dict:
        """Run custom diagnostic check.

        For non-standard components, this method generates a diagnostic
        report by examining component-specific log files.
        """
        result = {"status": "unknown", "component": component_name}

        # Look for component-specific log file
        log_dir = Path("/var/log/app")
        component_log = log_dir / f"{component_name}.log"

        try:
            if component_log.exists():
                # Read last 50 lines of component log
                with open(component_log, "r") as f:
                    lines = f.readlines()[-50:]
                result["log_entries"] = "".join(lines)
                result["status"] = "ok"
            else:
                result["status"] = "no_log_file"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result
