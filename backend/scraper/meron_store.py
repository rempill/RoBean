import asyncio

from pydantic import HttpUrl

from scraper.schemas import CoffeeBean
from scraper.utils import get_response
import json
import re

# Matches patterns like "250g", "1kg", "500 gr" (case-insensitive)
WEIGHT_PATTERN = re.compile(r"(\d+)\s*(kg|g|gr)", re.IGNORECASE)

def extract_grams(text:str)-> int:
    if not text:
        return 0
    match=WEIGHT_PATTERN.search(text)
    if not match:
        return 0
    value,unit=match.groups()
    value=int(value)
    return value*1000 if unit.lower()=="kg" else value

async def parse_meron_product(product):
    full_name = product["name"]

    excluded_keywords=["Gift Card", "Box", "Meron"]
    if any(word in full_name for word in excluded_keywords) or product.get("type")=="pw-gift-card":
        return None

    description = product.get("description", "")

    # Remove noise and take part before '|' if exists
    name_part = full_name.split("|")[0].strip()
    clean_name = re.sub(r"\s+\d+(g|kg|gr).*$", "", name_part, flags=re.IGNORECASE).strip()
    clean_name = clean_name.replace(" &#8211;", "").replace(" House", "").strip()

    # Extract grams, fallback to description if not found in name
    grams=extract_grams(full_name) or extract_grams(description)

    if grams==0:
        print(f"Skipping non-coffee or unknown weight: {full_name}")
        return None

    try:
        price=round(float(product["prices"]["price"])/100, 2)
        price_per_gram=round(price/grams, 3)
        url=HttpUrl(product["permalink"])
        image=HttpUrl(product["images"][0]["src"]) if product["images"] else None
        return CoffeeBean(
            name=clean_name,
            store="Meron",
            url=url,
            image=image,
            variants=[{
                "grams": grams,
                "price": price,
                "price_per_gram": price_per_gram
            }]
        )
    except (ValueError,KeyError,ZeroDivisionError):
        print(f"Invalid price for product: {full_name}")
        return None


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
        bean=await parse_meron_product(product)
        if not bean:
            continue
        # Grouping by name to handle different bag sizes
        if bean.name in beans:
            beans[bean.name].variants.extend(bean.variants)
            # If multiple sizes exist, update URL to a search result for better UX
            search_query=bean.name.replace(" ","+")
            beans[bean.name].url = f"https://meron.ro/?s={search_query}&post_type=product"
        else:
            beans[bean.name] = bean
    return list(beans.values())
