"""Feedback API module for user feedback and comments."""

from flask import Blueprint, request, render_template_string

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")


@feedback_bp.route("/preview", methods=["GET", "POST"])
def preview_feedback():
    """Preview feedback before submission.

    Renders user's feedback message in an HTML preview.
    """
    if request.method == "POST":
        message = request.form.get("message", "")
    else:
        message = request.args.get("message", "")

    # Render preview with user's message
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feedback Preview</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .preview-box {{
                border: 1px solid #ccc;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 4px;
            }}
            h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h2>Your Feedback Preview</h2>
        <div class="preview-box">
            {message}
        </div>
        <p><small>This is how your feedback will appear.</small></p>
    </body>
    </html>
    """
    return render_template_string(html_template)


@feedback_bp.route("/search", methods=["GET"])
def search_feedback():
    """Search through feedback entries.

    Returns HTML page with search results.
    """
    query = request.args.get("q", "")

    # Simulated search results (would come from DB in real app)
    results = [
        {"id": 1, "author": "User1", "message": "Great product!"},
        {"id": 2, "author": "User2", "message": "Needs improvement"},
    ]

    # Filter results (simplified)
    if query:
        results = [r for r in results if query.lower() in r["message"].lower()]

    # Build HTML response with search term highlighted
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feedback Search</title>
    </head>
    <body>
        <h1>Search Results for: {query}</h1>
        <ul>
    """

    for r in results:
        html += f"<li><strong>{r['author']}</strong>: {r['message']}</li>"

    html += """
        </ul>
    </body>
    </html>
    """
    return html


@feedback_bp.route("/error", methods=["GET"])
def error_page():
    """Display error message to user."""
    error_msg = request.args.get("msg", "Unknown error")

    return f"""
    <html>
    <head><title>Error</title></head>
    <body>
        <h1 style="color: red;">Error Occurred</h1>
        <p>Error details: {error_msg}</p>
        <a href="/">Return to home</a>
    </body>
    </html>
    """
