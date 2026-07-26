import asyncio
import json
import logging
from pydantic import HttpUrl

from scraper.schemas import ScrapedBean
from scraper.utils import get_response

logger = logging.getLogger(__name__)

EMBU_STORE_NAME = "Embu Coffee"
EMBU_API_URL = "https://embu-coffee.ro/collections/all/products.json"


async def scrape_embu_store() -> list[ScrapedBean]:
    try:
        response_text = await get_response(EMBU_API_URL)
        if not response_text:
            logger.warning(f"Empty or failed response from {EMBU_STORE_NAME} at {EMBU_API_URL}")
            return []

        try:
            payload = json.loads(response_text)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse JSON response from {EMBU_STORE_NAME} at {EMBU_API_URL}: {e}")
            return []

        if not isinstance(payload, dict):
            logger.warning(f"Unexpected JSON root type from {EMBU_STORE_NAME}: expected dict, got {type(payload).__name__}")
            return []

        products = payload.get("products")
        if not isinstance(products, list) or not products:
            logger.info(f"No products found or empty list in payload from {EMBU_STORE_NAME}")
            return []

        beans: list[ScrapedBean] = []

        for product in products:
            if not isinstance(product, dict):
                continue

            name = product.get("title")
            handle = product.get("handle")
            if not name or not handle:
                continue

            url = f"https://embu-coffee.ro/products/{handle}"
            images = product.get("images", [])
            image = images[0].get("src") if isinstance(images, list) and images and isinstance(images[0], dict) else None

            variants_json = product.get("variants")
            if not isinstance(variants_json, list) or not variants_json:
                logger.debug(f"No variants found for product '{name}' from {EMBU_STORE_NAME}")
                continue

            variants = []
            for variant_json in variants_json:
                if not isinstance(variant_json, dict):
                    continue

                option1 = variant_json.get("option1")
                price_val = variant_json.get("price")
                if not option1 or price_val is None:
                    continue

                try:
                    grams = int(str(option1).translate(str.maketrans("", "", "KkGg")).strip())
                    grams = 1000 if grams == 1 else grams
                    price = float(price_val)
                except (ValueError, TypeError):
                    logger.debug(f"Invalid variant option '{option1}' or price '{price_val}' for product '{name}'")
                    continue

                if grams <= 0 or price <= 0:
                    continue

                if grams in [v["weight_grams"] for v in variants]:
                    continue

                price_per_gram = round(price / grams, 3)
                variants.append({
                    "weight_grams": grams,
                    "price": price,
                    "price_per_gram": price_per_gram,
                })

            if not variants:
                continue

            try:
                scraped_bean = ScrapedBean(
                    name=str(name).strip(),
                    store_name=EMBU_STORE_NAME,
                    url=HttpUrl(url),
                    image_url=HttpUrl(image) if image else None,
                    variants=variants,
                )
                beans.append(scraped_bean)
            except Exception as val_err:
                logger.warning(f"Validation error creating ScrapedBean for '{name}': {val_err}")
                continue

        return beans

    except Exception as exc:
        logger.error(f"Unhandled error while scraping {EMBU_STORE_NAME} ({EMBU_API_URL}): {exc}", exc_info=True)
        return []


if __name__ == "__main__":
    beans=asyncio.run(scrape_embu_store())
    for bean in beans:
        print(bean)