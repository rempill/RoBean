import asyncio
import inspect
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import BeanUpsertData, VariantUpsertData, upsert_coffee_bean
from db.database import SessionLocal, init_db
from db.models import Bean, Store
from scraper import SCRAPERS


async def scrape_store(store: Store, db: AsyncSession) -> None:
    scraper = SCRAPERS.get(store.name)

    if scraper is None:
        return

    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=2)

    try:
        beans = await (scraper() if inspect.iscoroutinefunction(scraper) else asyncio.to_thread(scraper))
    except Exception as e:
        print(f"Error scraping {store.name}: {e}")
        return

    if not beans:
        print(f"No beans found for {store.name}. Skipping.")
        return

    for bean in beans:
        bean_data: BeanUpsertData = {
            "store_id": store.id,
            "name": bean.name,
            "url": str(bean.url),
            "image": str(bean.image) if getattr(bean, "image", None) else None,
        }
        variants: list[VariantUpsertData] = [
            {
                "grams": variant.grams,
                "price": variant.price,
                "price_per_gram": variant.price_per_gram,
            }
            for variant in bean.variants
        ]
        await upsert_coffee_bean(db, bean_data, variants)

    await db.execute(
        update(Bean)
        .where(
            Bean.store_id == store.id,
            (Bean.last_seen.is_(None)) | (Bean.last_seen < cutoff)
        )
        .values(is_active=False)
    )


async def run_all_scrapers() -> None:
    async with SessionLocal() as db:
        result = await db.execute(select(Store))
        stores = result.scalars().all()
        if not stores:
            print("No stores found after seeding. Aborting.")
            return
        for store in stores:
            await scrape_store(store, db)
        await db.commit()


async def main() -> None:
    await run_all_scrapers()


if __name__ == "__main__":
    asyncio.run(main())
