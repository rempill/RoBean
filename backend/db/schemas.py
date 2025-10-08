from pydantic import BaseModel
from datetime import datetime

class StoreOut(BaseModel):
    id: int
    name: str
    url: str | None = None
    class Config:
        from_attributes = True

class VariantOut(BaseModel):
    grams: int
    price: float
    price_per_gram: float | None = None
    class Config:
        from_attributes = True

class CoffeeBeanOut(BaseModel):
    id: int
    name: str
    store_id: int
    store: StoreOut
    url: str
    image: str | None
    variants: list[VariantOut]
    updated_at: datetime
    class Config:
        from_attributes = True

class BeansResponse(BaseModel):
    beans: list[CoffeeBeanOut]
