import asyncio
import inspect
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from db.crud import BeanUpsertData, VariantUpsertData, upsert_coffee_bean
from db.database import SessionLocal, init_db
from db.models import Bean, Store
from scraper import SCRAPERS
from scraper.schemas import ScrapedBean

logger = logging.getLogger(__name__)


async def validate_and_save_bean(raw_bean_data: dict, db_session: AsyncSession) -> bool:
    try:
        validated_bean = ScrapedBean.model_validate(raw_bean_data)
    except ValidationError as e:
        url = raw_bean_data.get("url", "unknown url") if isinstance(raw_bean_data, dict) else "unknown url"
        logger.warning(f"Validation failed for bean at {url}:\n{e}")
        return False
    except Exception as e:
        url = raw_bean_data.get("url", "unknown url") if isinstance(raw_bean_data, dict) else "unknown url"
        logger.warning(f"Unexpected error validating bean at {url}:\n{e}")
        return False

    store_stmt = select(Store).where(Store.name == validated_bean.store_name)
    store_result = await db_session.execute(store_stmt)
    store = store_result.scalar_one_or_none()
    
    if not store:
        logger.warning(f"Store '{validated_bean.store_name}' not found in DB.")
        return False

    bean_data: BeanUpsertData = {
        "store_id": store.id,
        "name": validated_bean.name,
        "url": str(validated_bean.url),
        "image": str(validated_bean.image_url) if validated_bean.image_url else None,
    }
    
    variants: list[VariantUpsertData] = [
        {
            "grams": variant.weight_grams,
            "price": variant.price,
            "price_per_gram": variant.price_per_gram,
        }
        for variant in validated_bean.variants
    ]
    
    try:
        await upsert_coffee_bean(db_session, bean_data, variants)
        return True
    except Exception as e:
        logger.warning(f"Database error while saving bean at {validated_bean.url}:\n{e}")
        return False


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
        if hasattr(bean, "model_dump"):
            raw_bean_data = bean.model_dump()
        elif hasattr(bean, "__dict__"):
            raw_bean_data = vars(bean)
        else:
            raw_bean_data = bean
            
        await validate_and_save_bean(raw_bean_data, db)

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
