from pathlib import Path

import os
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Always load the backend .env file regardless of current working directory.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)

class Base(DeclarativeBase):
    pass

DB_PATH = BACKEND_DIR / "robean.db"

DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    sqlite_prefixes = ("sqlite+aiosqlite:///", "sqlite:///")
    for prefix in sqlite_prefixes:
        if database_url.startswith(prefix):
            db_location = database_url[len(prefix) :]
            if db_location.startswith("./") or db_location.startswith(".\\"):
                absolute_path = (BACKEND_DIR / db_location[2:]).resolve()
                return f"{prefix}{absolute_path.as_posix()}"
            return database_url
    return database_url


DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))

engine_kwargs = {"echo": False, "future": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from db import models as _models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db_path() -> Path:
    for sqlite_prefix in ("sqlite+aiosqlite:///", "sqlite:///"):
        if DATABASE_URL.startswith(sqlite_prefix):
            return Path(DATABASE_URL[len(sqlite_prefix) :])
    return DB_PATH
