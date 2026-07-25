#!/bin/sh
echo "Initializing database..."
python -c "import asyncio; from db.database import init_db; asyncio.run(init_db())"
echo "Running database migrations..."
alembic upgrade head
celery -A celery_stuff.celery_app:celery worker --loglevel=info --pool=threads &
celery -A celery_stuff.celery_app:celery beat --loglevel=info &
exec uvicorn main:app --host 0.0.0.0 --port 8000