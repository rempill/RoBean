from celery import Celery
from ..run_scrapers import run_all_scrapers
from ..db.database import SessionLocal
from asgiref.sync import async_to_sync
from .config import beat_schedule, timezone

celery = Celery(
    "robean",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.beat_schedule = beat_schedule
celery.conf.timezone = timezone

async def _refresh_db():
    async with SessionLocal() as db:
        await run_all_scrapers(db)

@celery.task
def refresh_db():
    # Converts async function to sync safely on Windows
    async_to_sync(_refresh_db)()