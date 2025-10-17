import asyncio

from pydantic import HttpUrl

from scraper.schemas import CoffeeBean
from scraper.utils import get_response
import json

async def scrape_embu_store():
    embu_api="https://embu-coffee.ro/collections/all/products.json"
    response_text=await get_response(embu_api)
    if not response_text:
        return []
    try:
        products=json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to parse JSON response from EMBU")
        return []

    beans=[]

    for product in products.get("products", []):
        name=product["title"]
        url="https://embu-coffee.ro/products/"+product["handle"]
        image=product["images"][0]["src"] if product["images"] else None
        variants_json=product["variants"]
        if not variants_json:
            print(f"No variants found for product: {name}")
            continue
        variants=[]
        for variant_json in variants_json:
            try:
                grams=int(variant_json["option1"].translate(str.maketrans('','','Kkg')).strip())
                grams=1000 if grams==1 else grams
                price=float(variant_json["price"])
            except ValueError:
                print(f"Invalid data for variant in product: {name}")
                continue
            if grams in [v["grams"] for v in variants]:
                    continue
            price_per_gram=round(price/grams,3)
            variant={
                "grams": grams,
                "price": price,
                "price_per_gram": price_per_gram
            }
            variants.append(variant)
        if not variants:
            print(f"No valid variants for product: {name}")
            continue
        beans.append(CoffeeBean(
            name=name,
            store="Embu Coffee",
            url=HttpUrl(url),
            image=HttpUrl(image) if image else None,
            variants=variants
        ))

    return beans

if __name__ == "__main__":
    beans=asyncio.run(scrape_embu_store())
    for bean in beans:
        print(bean)