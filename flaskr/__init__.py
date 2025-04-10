import os
from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Default secret key used for development only.
        # Should be overridden with a random value for deployment.
        SECRET_KEY="dev",
        # You can add default database config here later if needed
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        # Example: Load config from instance/config.py
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    # Flask doesn't create the instance folder automatically,
    # but it should exist for config files or the SQLite database.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # Already exists or permission error

    # Register blueprints/routes here
    from . import routes

    app.register_blueprint(routes.bp)
    # Add other initializations like database, auth later

    # A simple health check route (optional)
    @app.route("/health")
    def health():
        return "OK"

    return app
