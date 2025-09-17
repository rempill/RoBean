import asyncio
import inspect
from sqlalchemy import select
from db.database import SessionLocal, init_db
from db.models import Store
from scraper import SCRAPERS
from db.crud import upsert_coffee_bean


async def scrape_store(store, db):
    scraper = SCRAPERS.get(store.name)

    beans = await (scraper() if inspect.iscoroutinefunction(scraper) else asyncio.to_thread(scraper))

    for bean in beans:
        bean_data = {
            "store_id": store.id,
            "name": bean.name,
            "url": str(bean.url),
            "image": str(bean.image) if getattr(bean, "image", None) else None,
        }
        variants = [v.model_dump() for v in bean.variants]
        print(bean_data)
        await upsert_coffee_bean(db, bean_data, variants)


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
