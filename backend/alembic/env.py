import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Ensure `backend/` is on sys.path so `db.*` imports work no matter where alembic is run from.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import models so metadata is populated for autogenerate.
from db.database import DATABASE_URL, Base  # noqa: E402
from db import models  # noqa: F401,E402

# Alembic migration context is sync. For SQLite, convert async URL to sync URL.
DATABASE_URL_SYNC = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    # If alembic.ini isn't aligned with DATABASE_URL, fall back to the app's URL.
    if not url:
        url = DATABASE_URL_SYNC

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        DATABASE_URL_SYNC,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
