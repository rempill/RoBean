from celery import Celery, signals
from scripts.run_scrapers import run_all_scrapers
from asgiref.sync import async_to_sync
from .config import beat_schedule, timezone
from scripts.seed_stores import main as seed_stores_main
import os

redis_url = os.getenv("REDIS_URL") or os.getenv("CELERY_BROKER_URL") or "redis://localhost:6379/0"

celery = Celery(
    "robean",
    broker=redis_url,
    backend=redis_url
)

celery.conf.beat_schedule = beat_schedule
celery.conf.timezone = timezone

async def _refresh_db():
    # Seed stores first to ensure there is something to scrape
    await seed_stores_main()
    # Then run scrapers sequentially
    await run_all_scrapers()

@celery.task(name="celery_stuff.celery_app.refresh_db")
def refresh_db() -> None:
    # Converts async function to sync safely on Windows and in workers
    async_to_sync(_refresh_db)()