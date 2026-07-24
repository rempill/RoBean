from pydantic import BaseModel, HttpUrl, Field
from typing import List

class ScrapedVariant(BaseModel):
    weight_grams: int = Field(gt=0, description="Weight of the variant in grams")
    price: float = Field(gt=0, description="Price of the variant")
    price_per_gram: float = Field(gt=0, description="Price per gram")

class ScrapedBean(BaseModel):
    store_name: str = Field(min_length=1, description="Name of the store")
    name: str = Field(min_length=1, description="Name of the coffee bean")
    url: HttpUrl = Field(description="URL of the product page")
    image_url: HttpUrl = Field(description="URL of the product image")
    variants: List[ScrapedVariant] = Field(min_length=1, description="List of available variants")
