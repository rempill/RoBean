from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Bean, Variant


class BeanUpsertData(TypedDict):
    store_id: int
    name: str
    url: str
    image: str | None


class VariantUpsertData(TypedDict):
    grams: int
    price: float | Decimal | None
    price_per_gram: float | Decimal | None


async def upsert_coffee_bean(
    db: AsyncSession,
    data: BeanUpsertData,
    variants: Sequence[VariantUpsertData],
) -> int:
    now_utc = datetime.now(timezone.utc)

    stmt = select(Bean).where(
        Bean.store_id == data["store_id"],
        Bean.url == data["url"],
    )
    result = await db.execute(stmt)
    bean = result.scalar_one_or_none()

    if bean:
        bean.name = data["name"]
        bean.image = data.get("image")
        bean.is_active = True
        bean.last_seen = now_utc

        await db.execute(delete(Variant).where(Variant.bean_id == bean.id))
    else:
        bean = Bean(**data)
        bean.is_active = True
        bean.last_seen = now_utc

        db.add(bean)
        await db.flush()

    if variants:
        stmt = insert(Variant).values(
            [{"bean_id": bean.id, **variant} for variant in variants]
        )
        await db.execute(stmt)

    await db.flush()
    return bean.id
