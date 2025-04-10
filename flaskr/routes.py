from flask import Blueprint, render_template

# Use a Blueprint to organize routes
# This allows registering them in the app factory (__init__.py)
bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/")
def index():
    """Serves the main index page."""
    # Render the basic HTML template
    return render_template("index.html")
