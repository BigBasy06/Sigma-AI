#!/bin/sh
set -e

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 "flaskr:create_app()"
