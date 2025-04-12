# --- Build Stage ---
FROM python:3.10-slim-bullseye as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Upgrade pip and install essential build tools needed for building wheels
RUN python -m pip install --upgrade pip wheel setuptools && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

# ---> FIX THIS LINE <---
# Build wheels for all dependencies defined in requirements.txt
# Store the built wheels in /app/wheels, do not install them here.
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt
# ^^^ Changed 'install' to 'wheel'

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

# Copy built wheels from builder stage
COPY --from=builder /app/wheels /wheels
# Copy requirements.txt is no longer needed here if installing from wheels directly
# COPY --from=builder /app/requirements.txt .

# Install dependencies from the pre-built wheels
RUN pip install --no-cache-dir /wheels/*
# ^^^ Use --no-cache-dir consistently (old --no-cache is deprecated)

# Copy the application code
# Ensure .dockerignore is set up to exclude .git, venv, __pycache__, etc.
COPY . .
COPY start.sh .
RUN chmod +x start.sh

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port the app runs on (Gunicorn will bind to $PORT provided by Render)
# Render injects the PORT environment variable, typically 10000
# EXPOSE 10000 # Not strictly necessary as Render maps automatically, but good practice

# Define the command to run the application using Gunicorn
# Render's "Start Command" will override this, but it's good to have a default.
# The actual start command in Render will be "sh start.sh"
CMD ["sh", "start.sh"]
