import asyncio

from pydantic import HttpUrl

from scraper.schemas import CoffeeBean
from scraper.utils import get_response
import json


async def parse_kune_product(product):
    split_name = product["name"].split("|")
    name = split_name[0].replace(" &#8211;", "").replace(" House", "").strip()
    grams = split_name[1].replace("kg", "000").replace("g", "").strip()
    price = product["prices"]["price"]
    try:
        grams = int(grams)
        price = round(float(price) / 100, 2)
        price_per_gram = round(price / grams, 3)
        url = HttpUrl(product["permalink"])
        image = HttpUrl(product["images"][0]["src"]) if product["images"] else None
    except ValueError:
        print(f"Invalid data for Kune product: {product['name']}")
        return None
    variant = [{
        "grams": grams,
        "price": price,
        "price_per_gram": price_per_gram
    }]
    return CoffeeBean(
        name=name,
        store="Meron",
        url=url,
        image=image,
        variants=variant
    )


async def parse_meron_product(product):
    split_name = product["name"].split("|")
    name_and_grams = split_name[0].replace(" &#8211;", "").strip()
    name = " ".join(name_and_grams.split(" ")[:-1])
    grams = name_and_grams.split(" ")[-1]
    price = product["prices"]["price"]
    try:
        grams = int(grams.replace("kg", "000").replace("g", "").strip())
        price = round(float(price) / 100, 2)
        price_per_gram = round(price / grams, 3)
        url = HttpUrl(product["permalink"])
        image = HttpUrl(product["images"][0]["src"]) if product["images"] else None
    except ValueError:
        print(f"Invalid data for Meron product: {product['name']}")
        return None
    variant = [{
        "grams": grams,
        "price": price,
        "price_per_gram": price_per_gram
    }]
    return CoffeeBean(
        name=name,
        store="Meron",
        url=url,
        image=image,
        variants=variant
    )


async def scrape_meron_store():
    meron_api = "https://meron.ro/wp-json/wc/store/products?category=cafea&per_page=100"
    response_text = await get_response(meron_api)
    if not response_text:
        return []
    try:
        products = json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to parse JSON response from Meron")
        return []

    beans = {}

    for product in products:
        full_name = product["name"]
        if "Meron" in full_name or "Box" in full_name:
            continue

        if "Kune" in full_name:
            bean = await parse_kune_product(product)
        else:
            bean = await parse_meron_product(product)
        if not bean:
            continue
        bean_name = bean.name
        if bean_name in beans:
            beans[bean_name].variants.extend(bean.variants)
        else:
            beans[bean_name] = bean
        if len(beans[bean_name].variants) > 1:
            beans[bean_name].url = "https://meron.ro/?s=" + bean_name.replace(" ", "+") + "&post_type=product"

    return list(beans.values())
