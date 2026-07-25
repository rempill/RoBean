#!/bin/sh
echo "Running database migrations..."
alembic upgrade head

echo "Seeding stores synchronously..."
python -m scripts.seed_stores

celery -A celery_stuff.celery_app:celery worker --loglevel=info --pool=threads &
celery -A celery_stuff.celery_app:celery beat --loglevel=info &
exec uvicorn main:app --host 0.0.0.0 --port 8000