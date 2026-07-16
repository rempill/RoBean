from datetime import datetime
from pydantic import BaseModel, ConfigDict

class VariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    grams: int
    price: float | None = None
    price_per_gram: float | None = None


class CoffeeBeanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    image: str | None = None
    variants: list[VariantOut]
    updated_at: datetime


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str | None = None
    beans: list[CoffeeBeanOut]


class Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stores: list[StoreOut]
