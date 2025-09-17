from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DB_PATH = Path(__file__).resolve().parent.parent / "robean.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"

Base=declarative_base()

engine=create_async_engine(DATABASE_URL,echo=False,future=True)

SessionLocal=async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db():
    from .models import Bean, Store,Variant
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_db_path():
    return DB_PATH


