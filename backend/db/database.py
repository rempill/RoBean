from pathlib import Path

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

Base=declarative_base()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH=BASE_DIR/"robean.db"

DEFAULT_DATABASE_URL=f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"
DATABASE_URL=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine=create_async_engine(DATABASE_URL,echo=False,future=True)

SessionLocal=async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db() -> None:
    return

def get_db_path() -> Path:
    return DB_PATH


