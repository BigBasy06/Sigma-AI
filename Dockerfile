# Dockerfile

# --- Build Stage ---
# Use an official Python runtime as a parent image
# Choose a specific version matching your development environment (e.g., 3.10)
FROM python:3.10-slim-bullseye as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed for Python packages (if any)
# Example: RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*
# Add any specific build dependencies for your project here if needed

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
# Add gunicorn (or waitress) for production serving - will be added to requirements.txt separately
# RUN echo "gunicorn" >> requirements.txt # We'll modify the actual file instead
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# --- Final Stage ---
# Use a slim Python image for the final container
FROM python:3.10-slim-bullseye as final

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=flaskr:create_app()
# Set FLASK_ENV via runtime environment variable (e.g., in Render), not here

WORKDIR /app

# Create a non-root user and group
RUN addgroup --system app && adduser --system --ingroup app app

# Copy installed dependencies from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy the application code
# Ensure .dockerignore is set up to exclude .git, venv, __pycache__, etc.
COPY . .

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port the app runs on (Gunicorn will bind to $PORT provided by Render)
# Render injects the PORT environment variable, typically 10000
# EXPOSE 10000 # Not strictly necessary as Render maps automatically, but good practice

# Define the command to run the application using Gunicorn
# Render's "Start Command" will override this, but it's good to have a default.
# The actual start command in Render will include migrations:
# flask db upgrade && gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 flaskr:create_app()
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "flaskr:create_app()"]
