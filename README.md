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
