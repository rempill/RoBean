from celery.schedules import crontab

beat_schedule={
    "refresh-db-every-day": {
        "task": "celery_stuff.celery_app.refresh_db",
        "schedule":crontab(hour=0,minute=0)
    },
}
timezone="UTC"