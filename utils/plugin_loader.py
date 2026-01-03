"""Plugin system for extensible data processing.

This module provides a plugin architecture for handling different
data formats and transformations. Plugins are registered handlers
that process data based on configured pipelines.
"""

import json
import base64
import hashlib
import zlib
from typing import Any, Callable, Dict, List, Optional
from functools import wraps
from datetime import datetime


class PluginRegistry:
    """Registry for data processing plugins."""

    _handlers: Dict[str, Callable] = {}
    _pipelines: Dict[str, List[str]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a handler function."""
        def decorator(func):
            cls._handlers[name] = func
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def get_handler(cls, name: str) -> Optional[Callable]:
        """Get a registered handler by name."""
        return cls._handlers.get(name)

    @classmethod
    def register_pipeline(cls, name: str, steps: List[str]):
        """Register a processing pipeline."""
        cls._pipelines[name] = steps

    @classmethod
    def get_pipeline(cls, name: str) -> List[str]:
        """Get pipeline steps."""
        return cls._pipelines.get(name, [])


# Built-in handlers
@PluginRegistry.register("base64_encode")
def _base64_encode(data: Any) -> str:
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


@PluginRegistry.register("base64_decode")
def _base64_decode(data: str) -> bytes:
    return base64.b64decode(data)


@PluginRegistry.register("json_encode")
def _json_encode(data: Any) -> str:
    return json.dumps(data)


@PluginRegistry.register("json_decode")
def _json_decode(data: str) -> Any:
    return json.loads(data)


@PluginRegistry.register("compress")
def _compress(data: Any) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return zlib.compress(data)


@PluginRegistry.register("decompress")
def _decompress(data: bytes) -> bytes:
    return zlib.decompress(data)


@PluginRegistry.register("hash_md5")
def _hash_md5(data: Any) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


@PluginRegistry.register("hash_sha256")
def _hash_sha256(data: Any) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


class DataProcessor:
    """Processes data through configured handlers and pipelines."""

    def __init__(self):
        self._cache = {}
        self._stats = {"processed": 0, "errors": 0}

    def process(self, data: Any, handler_name: str) -> Any:
        """Process data using a named handler."""
        handler = PluginRegistry.get_handler(handler_name)
        if handler:
            self._stats["processed"] += 1
            return handler(data)
        raise ValueError(f"Unknown handler: {handler_name}")

    def process_pipeline(self, data: Any, pipeline_name: str) -> Any:
        """Process data through a named pipeline."""
        steps = PluginRegistry.get_pipeline(pipeline_name)
        result = data
        for step in steps:
            result = self.process(result, step)
        return result

    def get_stats(self) -> dict:
        """Get processing statistics."""
        return self._stats.copy()


class TransformationEngine:
    """Advanced data transformation engine.

    Supports dynamic transformations based on configuration.
    Transformations can be chained and configured at runtime.
    """

    # Built-in transformation methods
    TRANSFORMS = {
        "uppercase": str.upper,
        "lowercase": str.lower,
        "strip": str.strip,
        "reverse": lambda s: s[::-1],
        "length": len,
    }

    def __init__(self):
        self._custom_transforms = {}
        self._history = []

    def add_transform(self, name: str, func: Callable):
        """Add a custom transformation."""
        self._custom_transforms[name] = func

    def transform(self, data: Any, transform_name: str) -> Any:
        """Apply a transformation to data."""
        self._history.append({
            "transform": transform_name,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Check built-in transforms first
        if transform_name in self.TRANSFORMS:
            return self.TRANSFORMS[transform_name](data)

        # Check custom transforms
        if transform_name in self._custom_transforms:
            return self._custom_transforms[transform_name](data)

        # Dynamic transform lookup - check if it's a method on the data
        if hasattr(data, transform_name):
            attr = getattr(data, transform_name)
            if callable(attr):
                return attr()
            return attr

        raise ValueError(f"Unknown transform: {transform_name}")

    def chain_transform(self, data: Any, transforms: List[str]) -> Any:
        """Apply multiple transformations in sequence."""
        result = data
        for t in transforms:
            result = self.transform(result, t)
        return result

    def get_history(self) -> List[dict]:
        """Get transformation history."""
        return self._history.copy()


class ConfigurableFormatter:
    """Formats data according to configurable templates.

    Supports field extraction and formatting based on
    dot-notation paths and format specifications.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._formatters = {
            "date": self._format_date,
            "number": self._format_number,
            "string": self._format_string,
            "bool": self._format_bool,
        }

    def _format_date(self, value: Any, spec: str = "") -> str:
        if isinstance(value, datetime):
            return value.strftime(spec or "%Y-%m-%d")
        return str(value)

    def _format_number(self, value: Any, spec: str = "") -> str:
        try:
            num = float(value)
            if spec:
                return f"{num:{spec}}"
            return str(num)
        except (TypeError, ValueError):
            return str(value)

    def _format_string(self, value: Any, spec: str = "") -> str:
        s = str(value)
        if spec == "upper":
            return s.upper()
        elif spec == "lower":
            return s.lower()
        elif spec == "title":
            return s.title()
        return s

    def _format_bool(self, value: Any, spec: str = "") -> str:
        return "true" if value else "false"

    def get_nested_value(self, data: dict, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        return current

    def format_value(self, value: Any, format_type: str, spec: str = "") -> str:
        """Format a value according to type and specification."""
        formatter = self._formatters.get(format_type, self._format_string)
        return formatter(value, spec)

    def format_template(self, data: dict, template: dict) -> dict:
        """Format data according to template configuration.

        Template format:
        {
            "output_field": {
                "source": "path.to.field",
                "type": "string|number|date|bool",
                "spec": "format_specification"
            }
        }
        """
        result = {}
        for output_key, field_config in template.items():
            source_path = field_config.get("source", output_key)
            format_type = field_config.get("type", "string")
            spec = field_config.get("spec", "")

            value = self.get_nested_value(data, source_path)
            result[output_key] = self.format_value(value, format_type, spec)

        return result

    def render_string(self, template_str: str, context: dict) -> str:
        """Render a template string with context values.

        Uses Python string formatting for simple variable substitution.
        Template variables use {key} syntax for basic replacement
        or {key.subkey} for nested access.

        Args:
            template_str: Template with {placeholder} variables
            context: Dictionary of values to substitute

        Returns:
            Rendered string with placeholders replaced
        """
        # Create a namespace object for attribute access in templates
        class Namespace:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        ns = Namespace(**context)

        # Use format() for substitution - supports {0.attr} syntax
        try:
            return template_str.format(ns, **context)
        except (KeyError, AttributeError, IndexError):
            # Fallback: try simple string substitution
            result = template_str
            for key, value in context.items():
                result = result.replace("{" + key + "}", str(value))
            return result
