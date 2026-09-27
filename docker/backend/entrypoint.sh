#!/bin/sh
# Apply database migrations, then hand off to the container's CMD (uvicorn).
set -e

echo "Running database migrations..."
alembic upgrade head

exec "$@"
