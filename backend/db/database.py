from pathlib import Path

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Always load the backend .env file regardless of current working directory.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)

Base = declarative_base()

DB_PATH = BACKEND_DIR / "robean.db"

DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"


def _normalize_database_url(database_url: str) -> str:
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

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db() -> None:
    return

def get_db_path() -> Path:
    sqlite_prefix = "sqlite+aiosqlite:///"
    if DATABASE_URL.startswith(sqlite_prefix):
        return Path(DATABASE_URL[len(sqlite_prefix) :])
    return DB_PATH


