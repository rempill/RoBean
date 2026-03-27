import asyncio
import inspect
import traceback
from datetime import datetime, timezone, timedelta
from sqlalchemy import select,update
from db.database import SessionLocal, init_db
from db.models import Store,Bean
from scraper import SCRAPERS
from db.crud import upsert_coffee_bean


async def scrape_store(store, db):
    scraper = SCRAPERS.get(store.name)

    if scraper is None:
        return

    now_utc=datetime.now(timezone.utc)
    cutoff=now_utc-timedelta(days=2)

    try:
        beans = await (scraper() if inspect.iscoroutinefunction(scraper) else asyncio.to_thread(scraper))
    except Exception as e:
        print(f"Error scraping {store.name}: {e}")
        return

    if not beans:
        print(f"No beans found for {store.name}. Skipping.")
        return

    for bean in beans:
        bean_data = {
            "store_id": store.id,
            "name": bean.name,
            "url": str(bean.url),
            "image": str(bean.image) if getattr(bean, "image", None) else None,
        }
        variants = [v.model_dump() for v in bean.variants]
        await upsert_coffee_bean(db, bean_data, variants)

    await db.execute(
        update(Bean)
        .where(
            Bean.store_id == store.id,
            (Bean.last_seen.is_(None)) | (Bean.last_seen < cutoff)
        )
        .values(is_active=False)
    )


async def run_all_scrapers():
    async with SessionLocal() as db:
        result = await db.execute(select(Store))
        stores = result.scalars().all()
        if not stores:
            print("No stores found after seeding. Aborting.")
            return
        for store in stores:
            await scrape_store(store, db)
        await db.commit()

async def main():
    await run_all_scrapers()

if __name__=="__main__":
    asyncio.run(main())
