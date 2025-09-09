from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert
from .models import Bean,Variant

async def upsert_coffee_bean(db:AsyncSession,data:dict,variants:list[dict]):
    # Check if bean exists
    stmt=select(Bean).where(
        Bean.store_id==data["store_id"],
        Bean.url==data["url"]
        )
    result=await db.execute(stmt)
    bean=result.scalar_one_or_none()

    if bean:
        bean.name=data["name"]
        bean.image=data.get("image")
    else:
        bean=Bean(**data)
        db.add(bean)

    # Replace variants without touching lazy relationship to avoid MissingGreenlet
    await db.execute(delete(Variant).where(Variant.bean_id == bean.id))

    if variants:
        stmt = insert(Variant).values([{"bean_id": bean.id, **v} for v in variants])
        await db.execute(stmt)
    # Flush so rows are written within the current transaction
    await db.flush()
    return bean.id
