# Sigma AI Project

This is the foundational setup for the Sigma AI adaptive learning platform.

## Setup Instructions

1.  **Clone the Repository (if applicable):**

    ```bash
    git clone <your-repository-url>
    cd sigma_ai_project
    ```

2.  **Create and Activate Virtual Environment:**
    This project uses `venv` for dependency management.

    ```bash
    # Create the virtual environment (only needs to be done once)
    python -m venv .venv

    # Activate the virtual environment
    # Windows (Command Prompt):
    # .venv\Scripts\activate
    # Windows (Git Bash / PowerShell):
    # source .venv/Scripts/activate
    # macOS / Linux:
    source .venv/bin/activate
    ```

    Your terminal prompt should now start with `(.venv)`.

3.  **Install Dependencies:**
    Install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Pre-commit Hooks:**
    This sets up automatic code formatting (black) and linting (flake8) checks before each commit.
    ```bash
    pre-commit install
    ```

## Running the Application

1.  **Ensure Virtual Environment is Active:** (See step 2 above).
2.  **Run the Flask Development Server:**
    ```bash
    python main.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5000/` or `http://localhost:5000/`. You should see the "Hello World from Sigma AI!" message.

## Initial Git Commit (If setting up from scratch)

If you followed these steps to create the project initially:

```bash
git add .
git commit -m "P1.1: Initial project foundational setup with Flask, Git, pre-commit"
```

## Authentication & Session Management

This application uses Flask-Login and Flask-Session for secure server-side session management.

### Configuration

Session behavior is configured via environment variables or `instance/config.py`. Key variables:

* `SECRET_KEY`: **Required and must be kept secret.** Used to sign session cookies. Set via `.env` or environment variable.
* `SESSION_TYPE`: How sessions are stored (e.g., `filesystem`, `redis`, `sqlalchemy`). Defaults to `filesystem`.
* `SESSION_PERMANENT`: Set to `False` for session expiry on browser close (recommended).
* `SESSION_USE_SIGNER`: Set to `True` to sign session cookie ID.
* `SESSION_FILE_DIR`: Directory for `filesystem` sessions (defaults to `instance/flask_session`).
* `SESSION_COOKIE_HTTPONLY`: Set to `True` (default).
* `SESSION_COOKIE_SAMESITE`: Set to `'Lax'` (default) or `'Strict'`.
* `SESSION_COOKIE_SECURE`: Set to `True` if your application is served over HTTPS (recommended for production).

See `.env.example` for setting these locally.

### Usage

* **Login:** Access the `/auth/login` page.
* **Logout:** Access the `/auth/logout` page (must be logged in).
* **Protected Routes:** Routes decorated with `@login_required` (from `flask_login`) require the user to be logged in. They will be redirected to the login page otherwise.
* **Current User:** Within routes, the logged-in user object is available via `from flask_login import current_user`. `current_user.is_authenticated` will be `True` if logged in.
