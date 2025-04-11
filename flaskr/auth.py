# flaskr/auth.py
"""
Authentication blueprint using Flask-Login and server-side sessions.
Handles login, logout, and user loading.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    # session, # Not used directly
    # current_app, # Not used directly
)
from sqlalchemy import select  # For modern query style
from flask_login import (
    # LoginManager, # Not used directly
    login_user,
    logout_user,
    login_required,
    current_user,  # Proxy for the currently logged-in user object
)

# from werkzeug.security import check_password_hash # Not used directly

# Import your User model and potentially CRUD functions
from .models import User
from . import db  # Import db for session access

# from . import crud # Or import specific functions like get_user_by_identifier

# Create Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Configure Flask-Login
# We need access to the LoginManager instance created in __init__.py
# One way is to pass it around, another is to use a function to get it,
# or configure the user_loader within create_app. Let's assume the latter.
# We still might need functions from crud here.


# --- Helper Function (Replace with crud import if preferred) ---
def get_user_by_identifier(identifier: str) -> User | None:
    """Gets a user by identifier using SQLAlchemy 2.0 style."""
    # Use db.session from the imported db instance
    stmt = select(User).where(User.user_identifier == identifier)
    return db.session.execute(stmt).scalar_one_or_none()
    # Or: return crud.get_user_by_identifier(db.session, identifier)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))  # Redirect if already logged in

    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")
        error = None
        user = get_user_by_identifier(identifier)  # Fetch user

        # Use a slightly more generic error message for security
        # (doesn't reveal if username exists)
        if user is None or not user.check_password(password):
            error = "Invalid credentials."
        # elif not user.check_password(password): # Combined above
        #     error = "Incorrect password."

        if error is None and user:  # Ensure user is not None here
            # Log the user in using Flask-Login
            # The second argument is 'remember me'
            login_user(user, remember=request.form.get("remember") == "on")
            flash("Login successful!", "success")
            # Redirect to the page they were trying to access, or index
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash(error, "error")

    # If GET request or login failed, show the login form
    # Create templates/auth/login.html
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required  # User must be logged in to log out
def logout():
    """Handles user logout."""
    logout_user()  # Clears the user session
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# --- Example Protected Route ---
# This demonstrates how @login_required works
@auth_bp.route("/profile")
@login_required
def profile():
    """A simple profile page accessible only to logged-in users."""
    # current_user is available here, provided by Flask-Login
    # Format string to fit within line length limits
    return (
        f"Hello, {current_user.user_identifier}! " f"Your user ID is {current_user.id}."
    )


# --- User Loader Callback ---
# This function needs to be registered with the LoginManager instance
# *within* create_app in __init__.py because it needs the LoginManager
# instance. We define it here for clarity, but registration happens
# in __init__.py.
def load_user(user_id: str) -> User | None:
    """User loader callback for Flask-Login. Converts user ID from session."""
    # Use db.session from the imported db instance
    try:
        user_id_int = int(user_id)
        # Use db.session.get for efficiency (identity map)
        return db.session.get(User, user_id_int)
        # Or: return crud.get_user_by_id(db.session, user_id_int)
    except ValueError:
        # If user_id is not a valid integer
        return None
