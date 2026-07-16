from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import BeanUpsertData, VariantUpsertData, upsert_coffee_bean
from scraper.schemas import CoffeeBean


async def save_scraped_bean(db: AsyncSession, store_id: int, scraped: CoffeeBean) -> int:
    bean_data: BeanUpsertData = {
        "name": scraped.name,
        "store_id": store_id,
        "url": str(scraped.url),
        "image": str(scraped.image) if scraped.image else None,
    }

    variants_data: list[VariantUpsertData] = []
    for v in scraped.variants:
        variants_data.append(
            {
                "grams": v.grams,
                "price": v.price,
                "price_per_gram": v.price_per_gram,
            }
        )

    return await upsert_coffee_bean(db, bean_data, variants_data)