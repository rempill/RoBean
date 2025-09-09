from sqlalchemy import String,Integer,Boolean,ForeignKey,DateTime,Text,UniqueConstraint, Float
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime,timezone
from .database import Base

def now_utc():
    return datetime.now(timezone.utc)

class Store(Base):
    __tablename__="stores"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(50),unique=True,nullable=False)
    url: Mapped[str | None]=mapped_column(String(2048))
    beans: Mapped[list["Bean"]]=relationship(back_populates="store")

class Bean(Base):
    __tablename__="beans"
    id: Mapped[int]=mapped_column(primary_key=True)
    store_id: Mapped[int]=mapped_column(ForeignKey("stores.id"))
    store: Mapped["Store"]=relationship(back_populates="beans")
    name: Mapped[str]=mapped_column(String(50),nullable=False)
    url: Mapped[str]=mapped_column(String(2048),nullable=False)
    image: Mapped[str | None]=mapped_column(String(2048))
    variants: Mapped[list["Variant"]]=relationship(back_populates="bean",cascade="all, delete-orphan")

    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now_utc)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now_utc, onupdate=now_utc)

class Variant(Base):
    __tablename__="variants"
    id:Mapped[int]=mapped_column(primary_key=True)
    grams:Mapped[int]=mapped_column(Integer,nullable=False)
    price:Mapped[int]=mapped_column(Integer,nullable=False)
    price_per_gram:Mapped[float]=mapped_column(Float,nullable=True)
    bean_id:Mapped[int]=mapped_column(ForeignKey("beans.id"))
    bean:Mapped["Bean"]=relationship(back_populates="variants")
