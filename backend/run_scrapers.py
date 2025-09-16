import asyncio
import inspect
from sqlalchemy import select
from db.database import SessionLocal
from db.models import Store
from scraper import SCRAPERS
from db.crud import upsert_coffee_bean


async def scrape_store(store, db):
    scraper = SCRAPERS.get(store.name)
    if not scraper:
        return

    if inspect.iscoroutinefunction(scraper):
        beans = await scraper()
    else:
        beans = await asyncio.to_thread(scraper)
    # Prepare all beans + variants first
    tasks = []
    for bean in beans:
        bean_data = {
            "store_id": store.id,
            "name": bean.name,
            "url": str(bean.url),
            "image": str(bean.image) if getattr(bean, "image", None) else None,
        }
        variants = [v.model_dump() for v in bean.variants]
        tasks.append(upsert_coffee_bean(db, bean_data, variants))
    # Run DB operations concurrently (if upsert_coffee_bean is async)
    await asyncio.gather(*tasks)

async def run_all_scrapers(db):
    async with SessionLocal() as db:
        result = await db.execute(select(Store))
        stores = result.scalars().all()
        await asyncio.gather(*(scrape_store(store, db) for store in stores))
        await db.commit()

async def main():
    async with SessionLocal() as db:
        await run_all_scrapers(db)
        await db.commit()

if __name__=="__main__":
    asyncio.run(main())