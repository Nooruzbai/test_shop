#!/bin/sh

set -e

SETUP_FLAG_FILE="/app/source/.setup_complete"

# Wait for the database to be ready
if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z db 5432; do
      sleep 0.1
    done
    echo "PostgreSQL is available."
fi

# Apply database migrations (this should always run)
echo "Applying database migrations..."
python manage.py migrate --no-input

# Check if the setup has already been completed.
if [ ! -f "$SETUP_FLAG_FILE" ]; then
    echo "First time setup: Loading initial data from fixtures..."

    # Load initial data from fixture files.
    # Replace with your actual fixture file names.
    python manage.py loaddata fixtures.json

    echo "Initial setup complete. Creating flag file."
    touch "$SETUP_FLAG_FILE"
else
    echo "Setup has already been completed. Skipping fixture loading."
fi

exec "$@"