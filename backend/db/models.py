from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    beans: Mapped[list["Bean"]] = relationship(back_populates="store")


class Bean(Base):
    __tablename__ = "beans"
    __table_args__ = (UniqueConstraint('store_id', 'name', name='_store_name_uc'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    store: Mapped["Store"] = relationship(back_populates="beans")
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    image: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    variants: Mapped[list["Variant"]] = relationship(
        back_populates="bean",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    grams: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_per_gram: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    bean_id: Mapped[int] = mapped_column(ForeignKey("beans.id"), nullable=False)
    bean: Mapped["Bean"] = relationship(back_populates="variants")
