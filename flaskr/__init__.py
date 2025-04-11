# flaskr/__init__.py
"""
Main Flask application factory and configuration module.
Initializes the Flask app, extensions (like SQLAlchemy, Flask-Migrate),
and registers blueprints. Implements configuration loading priority:
Defaults -> instance/config.py -> Environment Variables -> Test Config.
"""
import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session  # Import Flask-Session
from flask_login import LoginManager  # Import Flask-Login
from dotenv import load_dotenv  # Keep dotenv import here

# --- Instantiate extensions ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # Instantiate LoginManager
sess = Session()  # Instantiate Session

# Configure the default login view for @login_required
# Points to the login function within the 'auth' blueprint
login_manager.login_view = "auth.login"
# Optional: category for flash message when redirecting to login
login_manager.login_message_category = "info"


# --- Application Factory ---
def create_app(test_config=None):
    """
    Create and configure an instance of the Flask application.

    Args:
        test_config (dict, optional): Configuration mapping for testing.
                                      Defaults to None.

    Returns:
        Flask: The configured Flask application instance.
    """
    # --- Create Flask App Instance ---
    app = Flask(__name__, instance_relative_config=True)

    # --- Configuration Setup ---
    # Load dotenv here if using it
    load_dotenv()  # Load environment variables from .env

    instance_path = app.instance_path
    # ...(ensure instance_path exists)... # Handled later

    # Default config values
    default_db_path = os.path.join(instance_path, "flaskr.sqlite")
    db_uri = f"sqlite:///{default_db_path}"
    # For filesystem sessions
    default_session_dir = os.path.join(instance_path, "flask_session")

    app.config.from_mapping(
        SECRET_KEY="dev",  # MUST be overridden for production
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        GEMINI_API_KEY=None,
        # Flask-Session configuration
        # Default: filesystem. Alternatives: redis, sqlalchemy, mongodb
        SESSION_TYPE="filesystem",
        # Make sessions non-permanent (expire on browser close)
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,  # Sign session cookie identifiers
        SESSION_FILE_DIR=default_session_dir,  # Dir for filesystem sessions
        SESSION_COOKIE_HTTPONLY=True,  # Prevent client-side JS access
        # CSRF protection ('Strict' is more secure but can break links)
        SESSION_COOKIE_SAMESITE="Lax",
        # SET TO TRUE IN PRODUCTION WITH HTTPS!
        SESSION_COOKIE_SECURE=False,
        # Add other config like SESSION_REDIS if using Redis
    )

    # --- 2. Load Config from instance/config.py (if it exists) ---
    # Overrides defaults. silent=True prevents errors if file is missing.
    config_py_path = os.path.join(instance_path, "config.py")
    app.config.from_pyfile(config_py_path, silent=True)

    # --- 3. Load/Override from Environment Variables (Higher Priority) ---
    # Explicitly check for relevant env vars and update config if they are
    # set.
    env_vars_to_check = [
        "SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "GEMINI_API_KEY",
        "FLASK_ENV",
        "FLASK_DEBUG",
        "SESSION_TYPE",  # Add session vars
        # Add other expected env vars here (e.g., SESSION_FILE_DIR)
    ]
    for var in env_vars_to_check:
        value = os.getenv(var)
        if value is not None:
            # Handle type conversions if needed (e.g., FLASK_DEBUG)
            if var == "FLASK_DEBUG":
                app.config[var] = value.lower() in ["true", "1", "t"]
            # Add other type conversions as necessary
            # elif var == 'SOME_INTEGER_VAR':
            #     try:
            #         app.config[var] = int(value)
            #     except ValueError:
            #         app.logger.warning(f"Could not convert env var {var} to int.")
            else:
                app.config[var] = value
            # print(f"Loaded/Overrode {var} from environment variable.") # Debug print

    # Set SESSION_COOKIE_SECURE based on environment (example)
    if app.config.get("FLASK_ENV") == "production":
        app.config["SESSION_COOKIE_SECURE"] = True

    # --- 4. Load Test Config (if provided) ---
    # Overrides everything else, used specifically during testing.
    if test_config is not None:
        app.config.from_mapping(test_config)

    # --- Ensure Instance Folder and SESSION_FILE_DIR Exists ---
    try:
        os.makedirs(instance_path)
    except OSError:
        pass  # Already exists or permission error

    if app.config["SESSION_TYPE"] == "filesystem":
        try:
            os.makedirs(app.config["SESSION_FILE_DIR"])
        except OSError:
            pass  # Already exists

    # --- Initialize Extensions (MUST be after app creation and config) ---
    db.init_app(app)
    migrate.init_app(app, db)
    sess.init_app(app)  # Initialize Flask-Session
    login_manager.init_app(app)  # Initialize Flask-Login

    # --- Import Models (Necessary for discovery, AFTER extensions init) ---
    # pylint: disable=C0415,W0611 # Allow import here, suppress unused warning
    # noqa: F401 # Ruff/Flake8 ignore F401 (unused import) for models discovery
    from . import models  # noqa: F401

    # --- Import and Register Blueprints (AFTER extensions initialized) ---
    # pylint: disable=C0415 # Allow import here
    from . import routes
    from . import auth  # Import auth blueprint

    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.auth_bp)  # Register auth blueprint

    # --- Register User Loader Callback ---
    # MUST be done after login_manager is initialized
    from .auth import load_user  # Import the function defined in auth.py

    @login_manager.user_loader
    def user_loader_callback(user_id):
        return load_user(user_id)

    # --- Add CLI Commands (Optional) ---
    @app.cli.command("init-db-legacy")
    def init_db_command():
        """Clear existing data & create new tables (LEGACY - use migrations)."""
        click.echo("WARNING: Using legacy init-db. Flask-Migrate is preferred.")
        with app.app_context():
            db.create_all()
        click.echo("Initialized the database using db.create_all().")

    # --- Health Check Route (Optional) ---
    @app.route("/health")
    def health():
        """A simple health check endpoint."""
        return "OK"

    return app
