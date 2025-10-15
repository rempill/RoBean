from pydantic import BaseModel
from datetime import datetime
from typing import List

class VariantOut(BaseModel):
    grams: int
    price: float
    price_per_gram: float | None = None
    class Config:
        from_attributes = True

class CoffeeBeanOut(BaseModel):
    id: int
    name: str
    url: str
    image: str | None
    variants: List[VariantOut]
    updated_at: datetime
    class Config:
        from_attributes = True

class StoreOut(BaseModel):
    id: int
    name: str
    url: str | None = None
    beans: List[CoffeeBeanOut]
    class Config:
        from_attributes = True

class Response(BaseModel):
    stores: List[StoreOut]
