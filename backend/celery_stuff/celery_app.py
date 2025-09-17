from celery import Celery, signals
from scripts.run_scrapers import run_all_scrapers
from asgiref.sync import async_to_sync
from .config import beat_schedule, timezone
from scripts.seed_stores import main as seed_stores_main
import os

celery = Celery(
    "robean",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

celery.conf.beat_schedule = beat_schedule
celery.conf.timezone = timezone

async def _refresh_db():
    # Seed stores first to ensure there is something to scrape
    await seed_stores_main()
    # Then run scrapers sequentially
    await run_all_scrapers()

@celery.task
def refresh_db():
    # Converts async function to sync safely on Windows and in workers
    async_to_sync(_refresh_db)()

@signals.worker_ready.connect
def at_start(sender, **kwargs):
    # Enqueue once when worker is ready
    refresh_db.delay()