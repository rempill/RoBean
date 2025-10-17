from pydantic import BaseModel, HttpUrl
from typing import List

class Variant(BaseModel):
    grams: int
    price: float
    price_per_gram: float

class CoffeeBean(BaseModel):
    name: str
    store: str
    url: HttpUrl
    image: HttpUrl | None = None
    variants: List[Variant]

