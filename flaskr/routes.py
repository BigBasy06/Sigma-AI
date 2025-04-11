# flaskr/routes.py
"""
Defines the routes (views) for the application using a Blueprint.
Handles requests and interacts with models/templates.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for

# Import the database object and models if needed for DB operations
from . import db
from .models import User

# Create a Blueprint instance
# 'main' is the name of the blueprint
# url_prefix sets a prefix for all routes defined in this blueprint
bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/")
def index():
    """Serves the main index page."""
    # Example of querying the database (optional for basic index):
    # try:
    #     user_count = User.query.count()
    # except Exception as e:
    #     # Handle case where DB might not be initialized yet or connection issues
    #     flash(f"Database connection might be unavailable: {e}", "warning")
    #     user_count = 0

    # Render the HTML template found in the 'templates' folder
    return render_template(
        "index.html"
    )  # Add user_count=user_count if using the above example


# Example route showing basic DB interaction (add user form could POST here)
# @bp.route('/add_user', methods=('GET', 'POST'))
# def add_user():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         error = None
#
#         if not username:
#             error = 'Username is required.'
#         elif not email:
#             error = 'Email is required.'
#         elif User.query.filter_by(username=username).first() is not None:
#             error = f"User {username} is already registered."
#         elif User.query.filter_by(email=email).first() is not None:
#             error = f"Email {email} is already registered."
#
#         if error is None:
#             try:
#                 new_user = User(username=username, email=email)
#                 db.session.add(new_user)
#                 db.session.commit()
#                 flash(f"User {username} added successfully!", "success")
#                 return redirect(url_for('main.index')) # Redirect back to index after success
#             except Exception as e:
#                 db.session.rollback() # Roll back in case of error
#                 error = f"Failed to add user: {e}"
#
#         flash(error, "error") # Flash error message
#
#     # Render a template with a form for adding users (if GET request or POST failed)
#     return render_template('add_user.html') # You would need to create this template
