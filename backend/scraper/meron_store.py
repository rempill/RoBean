import asyncio
import json
import logging
import os
import re
from pydantic import HttpUrl

from scraper.schemas import ScrapedBean
from scraper.utils import get_response

logger = logging.getLogger(__name__)

MERON_STORE_NAME = "Meron"
MERON_API_URL = "https://meron.ro/wp-json/wc/store/products?category=cafea&per_page=100"
SCRAPENINJA_API_URL = "https://scrapeninja.apiroad.net/scrape"
SCRAPENINJA_API_KEY = os.getenv("SCRAPENINJA_API_KEY", "")

# Matches patterns like "250g", "1kg", "500 gr" (case-insensitive)
WEIGHT_PATTERN = re.compile(r"(\d+)\s*(kg|g|gr)", re.IGNORECASE)


def extract_grams(text: str | None) -> int:
    if not text:
        return 0
    match = WEIGHT_PATTERN.search(text)
    if not match:
        return 0
    value, unit = match.groups()
    value = int(value)
    return value * 1000 if unit.lower() == "kg" else value


async def parse_meron_product(product: dict) -> ScrapedBean | None:
    if not isinstance(product, dict):
        return None

    full_name = product.get("name")
    if not full_name:
        return None

    excluded_keywords = ["Gift Card", "Box", "Meron"]
    if any(word in full_name for word in excluded_keywords) or product.get("type") == "pw-gift-card":
        return None

    description = product.get("description", "") or ""

    # Remove noise and take part before '|' if exists
    name_part = full_name.split("|")[0].strip()
    clean_name = re.sub(r"\s+\d+(g|kg|gr).*$", "", name_part, flags=re.IGNORECASE).strip()
    clean_name = clean_name.replace(" &#8211;", "").replace(" House", "").strip()
    if not clean_name:
        return None

    # Extract grams, fallback to description if not found in name
    grams = extract_grams(full_name) or extract_grams(description)

    if grams <= 0:
        logger.debug(f"Skipping non-coffee or unknown weight: {full_name}")
        return None

    prices = product.get("prices")
    if not isinstance(prices, dict) or "price" not in prices or prices["price"] is None:
        logger.debug(f"Missing price dictionary for product: {full_name}")
        return None

    permalink = product.get("permalink")
    if not permalink:
        logger.debug(f"Missing permalink for product: {full_name}")
        return None

    images = product.get("images", [])
    image_src = images[0].get("src") if isinstance(images, list) and images and isinstance(images[0], dict) else None

    try:
        raw_price = float(prices["price"])
        price = round(raw_price / 100, 2)
        if price <= 0:
            return None
        price_per_gram = round(price / grams, 3)

        return ScrapedBean(
            name=clean_name,
            store_name=MERON_STORE_NAME,
            url=HttpUrl(permalink),
            image_url=HttpUrl(image_src) if image_src else None,
            variants=[{
                "weight_grams": grams,
                "price": price,
                "price_per_gram": price_per_gram,
            }],
        )
    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.debug(f"Invalid price or url data for product '{full_name}': {e}")
        return None


async def scrape_meron_store() -> list[ScrapedBean]:
    if not SCRAPENINJA_API_KEY:
        logger.error(f"SCRAPENINJA_API_KEY environment variable is missing for {MERON_STORE_NAME}")
        return []

    try:
        payload = {
            "url": MERON_API_URL,
            "headers": [
                "Accept: application/json",
                "Referer: https://meron.ro/",
            ],
        }
        headers = {
            "x-apiroad-key": SCRAPENINJA_API_KEY,
            "Content-Type": "application/json",
        }

        from curl_cffi.requests import AsyncSession

        async with AsyncSession(impersonate="chrome") as session:
            response = await session.post(
                SCRAPENINJA_API_URL,
                json=payload,
                headers=headers,
                timeout=20,
            )

        if response.status_code != 200:
            logger.error(
                f"ScrapeNinja proxy API returned non-200 status code {response.status_code} for {MERON_STORE_NAME}"
            )
            return []

        try:
            proxy_data = response.json()
            raw_body = proxy_data.get("body")
            if not raw_body:
                logger.error(f"ScrapeNinja response body is missing or empty for {MERON_STORE_NAME}")
                return []
            products = json.loads(raw_body)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.error(f"Failed to parse JSON response from ScrapeNinja for {MERON_STORE_NAME}: {e}")
            return []

        if not isinstance(products, list):
            logger.warning(f"Unexpected JSON root type from {MERON_STORE_NAME}: expected list, got {type(products).__name__}")
            return []

        beans: dict[str, ScrapedBean] = {}

        for product in products:
            bean = await parse_meron_product(product)
            if not bean:
                continue
            # Grouping by name to handle different bag sizes
            if bean.name in beans:
                beans[bean.name].variants.extend(bean.variants)
                search_query = bean.name.replace(" ", "+")
                beans[bean.name].url = HttpUrl(f"https://meron.ro/?s={search_query}&post_type=product")
            else:
                beans[bean.name] = bean

        return list(beans.values())

    except Exception as exc:
        logger.error(f"Unhandled error while scraping {MERON_STORE_NAME} via ScrapeNinja proxy ({MERON_API_URL}): {exc}", exc_info=True)
        return []


if __name__ == "__main__":
    beans = asyncio.run(scrape_meron_store())
    for bean in beans:
        print(bean)
