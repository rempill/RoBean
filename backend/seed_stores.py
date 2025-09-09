import asyncio

from sqlalchemy import select

from backend.db.database import SessionLocal, get_db_path, init_db
from backend.db.models import Store

stores = [
    {"name": "Embu", "url": "https://embu-coffee.ro/collections/all"},
]

async def main():
    print(f"Seeding at : {get_db_path()}")
    await init_db()
    async with SessionLocal() as db:
        for s in stores:
            exists = await db.execute(
                select(Store).where(Store.name == s["name"])
            )
            if not exists.scalar_one_or_none():
                db.add(Store(**s))
        await db.commit()
        print("Stores added successfully!")

if __name__ == "__main__":
    asyncio.run(main())
