#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Alembic migrations completed."

exec uvicorn main:app --host 0.0.0.0 --port 8000