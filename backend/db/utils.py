from .crud import upsert_coffee_bean
from ..models import CoffeeBean

# Converts a CoffeeBean object to a database entry and saves it
async def save_scraped_bean(db, store_id, scraped:CoffeeBean):
    bean_data={
        "name": scraped.name,
        "store_id":store_id,
        "url":str(scraped.url),
        "image":str(scraped.image) if scraped.image else None
    }

    variants_data=[]
    for v in scraped.variants:
        variants_data.append({
            "grams":v.grams,
            "price":v.price,
            "price_per_gram":v.price_per_gram
        })

    await upsert_coffee_bean(db,bean_data,variants_data)