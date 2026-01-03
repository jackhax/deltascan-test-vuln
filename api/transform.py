"""Data transformation API endpoints.

Provides endpoints for data processing and transformation
using the plugin system.
"""

from flask import Blueprint, request, jsonify
import json

from utils.plugin_loader import (
    DataProcessor,
    TransformationEngine,
    ConfigurableFormatter,
    PluginRegistry,
)

transform_bp = Blueprint("transform", __name__, url_prefix="/api/transform")

# Global instances
_processor = DataProcessor()
_engine = TransformationEngine()
_formatter = ConfigurableFormatter()


@transform_bp.route("/process", methods=["POST"])
def process_data():
    """Process data using a handler.

    Expected JSON body:
    {
        "data": "input data",
        "handler": "handler_name"
    }
    """
    body = request.get_json() or {}
    data = body.get("data")
    handler = body.get("handler")

    if not handler:
        return jsonify({"error": "Missing handler"}), 400

    try:
        result = _processor.process(data, handler)
        # Handle bytes result
        if isinstance(result, bytes):
            result = result.decode("utf-8", errors="replace")
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@transform_bp.route("/transform", methods=["POST"])
def transform_data():
    """Transform data using transformation engine.

    Expected JSON body:
    {
        "data": "input data",
        "transform": "transform_name"
    }

    Or for chained transforms:
    {
        "data": "input data",
        "transforms": ["transform1", "transform2"]
    }
    """
    body = request.get_json() or {}
    data = body.get("data")
    transform_name = body.get("transform")
    transform_chain = body.get("transforms")

    try:
        if transform_chain:
            result = _engine.chain_transform(data, transform_chain)
        elif transform_name:
            result = _engine.transform(data, transform_name)
        else:
            return jsonify({"error": "Missing transform or transforms"}), 400

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@transform_bp.route("/format", methods=["POST"])
def format_data():
    """Format data according to template.

    Expected JSON body:
    {
        "data": {"field": "value", ...},
        "template": {
            "output_field": {
                "source": "field",
                "type": "string",
                "spec": ""
            }
        }
    }
    """
    body = request.get_json() or {}
    data = body.get("data", {})
    template = body.get("template", {})

    try:
        result = _formatter.format_template(data, template)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@transform_bp.route("/handlers", methods=["GET"])
def list_handlers():
    """List available handlers."""
    return jsonify({
        "handlers": list(PluginRegistry._handlers.keys()),
        "transforms": list(TransformationEngine.TRANSFORMS.keys()),
    })


@transform_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get processing statistics."""
    return jsonify(_processor.get_stats())


@transform_bp.route("/history", methods=["GET"])
def get_history():
    """Get transformation history."""
    return jsonify({"history": _engine.get_history()})


@transform_bp.route("/pipeline", methods=["POST"])
def run_pipeline():
    """Run a registered pipeline.

    Expected JSON body:
    {
        "data": "input data",
        "pipeline": "pipeline_name"
    }
    """
    body = request.get_json() or {}
    data = body.get("data")
    pipeline = body.get("pipeline")

    if not pipeline:
        return jsonify({"error": "Missing pipeline name"}), 400

    try:
        result = _processor.process_pipeline(data, pipeline)
        if isinstance(result, bytes):
            result = result.decode("utf-8", errors="replace")
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@transform_bp.route("/extract", methods=["POST"])
def extract_field():
    """Extract a field from nested data.

    Expected JSON body:
    {
        "data": {"nested": {"field": "value"}},
        "path": "nested.field"
    }
    """
    body = request.get_json() or {}
    data = body.get("data", {})
    path = body.get("path", "")

    if not path:
        return jsonify({"error": "Missing path"}), 400

    result = _formatter.get_nested_value(data, path)
    return jsonify({"result": result})


@transform_bp.route("/render", methods=["POST"])
def render_template():
    """Render a template string with variables.

    Expected JSON body:
    {
        "template": "Hello {name}!",
        "variables": {"name": "World"}
    }

    Supports nested access: {user.email}
    """
    body = request.get_json() or {}
    template = body.get("template", "")
    variables = body.get("variables", {})

    if not template:
        return jsonify({"error": "Missing template"}), 400

    try:
        result = _formatter.render_string(template, variables)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
