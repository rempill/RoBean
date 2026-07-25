#!/bin/sh
celery -A celery_stuff.celery_app:celery worker --loglevel=info --pool=threads &
celery -A celery_stuff.celery_app:celery beat --loglevel=info &
exec uvicorn main:app --host 0.0.0.0 --port 8000