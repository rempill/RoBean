import asyncio
import re
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import HttpUrl

from scraper.schemas import CoffeeBean
from scraper.utils import get_response


BASE_URL = "https://yume.coffee"
SHOP_URL = f"{BASE_URL}/en_US/shop"

# Matches: "250g", "250 g", "250gr", "1kg", "1 kg"
WEIGHT_PATTERN = re.compile(r"(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>kg|g|gr)\b", re.IGNORECASE)

# Characters we don't want at the end of stored bean names
TRAILING_PUNCTUATION_RE = re.compile(r"[\s,;:|\-]+$")


def _parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    # Normalize: keep digits, dot, comma; then turn comma into dot.
    cleaned = re.sub(r"[^0-9,.]", "", text).strip()
    if not cleaned:
        return None

    # If both separators exist, assume comma is thousands separator in something like "1,234.56".
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", ".")

    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def _extract_grams(text: str) -> int:
    if not text:
        return 0
    m = WEIGHT_PATTERN.search(text)
    if not m:
        return 0
    value = m.group("value").replace(",", ".")
    unit = m.group("unit").lower()
    try:
        num = float(value)
    except ValueError:
        return 0

    if unit == "kg":
        return int(round(num * 1000))
    return int(round(num))


def _absolute_url(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return BASE_URL + href
    return BASE_URL + "/" + href


def _clean_bean_name(name: str) -> str:
    """Normalize a product display name into a stable bean name.

    - removes weight tokens (e.g. 250g)
    - collapses whitespace
    - strips trailing separators like commas/" - "/pipes
    """
    name = re.sub(WEIGHT_PATTERN, "", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.strip(" -|")
    name = TRAILING_PUNCTUATION_RE.sub("", name).strip()
    return name


def _parse_products_from_html(html: str) -> list[CoffeeBean]:
    soup = BeautifulSoup(html, "html.parser")

    beans: list[CoffeeBean] = []

    # Odoo shop cards typically use .oe_product_cart
    for card in soup.select(".oe_product_cart"):
        name_el = card.select_one('[itemprop="name"]')
        name = (name_el.get_text(strip=True) if name_el else "").strip()

        if not name:
            continue

        excluded_keywords = [
            "Gift",
            "Gift Card",
            "Merch",
            "Mug",
            "Cup",
            "T-shirt",
            "Voucher",
            "Equipment",
            "Brewer",
            "Filter",
            "Grinder",
            "Kettle",
        ]
        if any(k.lower() in name.lower() for k in excluded_keywords):
            continue

        a = card.select_one('a[itemprop="name"]') or card.select_one("a")
        url = _absolute_url(a.get("href") if a else None)
        if not url:
            continue

        price_el = card.select_one(".oe_currency_value")
        price = _parse_price(price_el.get_text(strip=True) if price_el else "")

        img_el = card.select_one("img")
        image = _absolute_url(img_el.get("src")) if img_el and img_el.get("src") else None

        grams = _extract_grams(name)
        if grams <= 0:
            continue

        if price is None or price <= 0:
            continue

        beans.append(
            CoffeeBean(
                name=re.sub(r"\s+", " ", name),
                store="Yume",
                url=HttpUrl(url),
                image=HttpUrl(image) if image else None,
                variants=[
                    {
                        "grams": grams,
                        "price": price,
                        "price_per_gram": round(price / grams, 3),
                    }
                ],
            )
        )

    return beans


def _find_next_page_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    # Prefer rel=next if present
    a = soup.select_one('a[rel="next"]')
    if a and a.get("href"):
        return _absolute_url(a.get("href"))

    # Fallback: look for anchors with text matching Next
    for cand in soup.select(".pagination a"):
        if cand.get_text(strip=True).lower() in {"next", "older", ">", "»"} and cand.get("href"):
            return _absolute_url(cand.get("href"))

    return None


async def scrape_yume_store(max_pages: int = 10) -> list[CoffeeBean]:
    """Scrape Yume shop page(s) and return CoffeeBean models."""

    url = SHOP_URL
    all_beans_by_key: dict[tuple[str, str], CoffeeBean] = {}

    for _ in range(max_pages):
        html = await get_response(url)
        if not html:
            break

        beans = _parse_products_from_html(html)
        for bean in beans:
            normalized_name = _clean_bean_name(bean.name)
            key = (normalized_name.lower(), bean.store)

            if key in all_beans_by_key:
                existing = all_beans_by_key[key]
                existing.variants.extend(bean.variants)
                existing.variants = sorted(
                    {v.grams: v for v in existing.variants}.values(), key=lambda v: v.grams
                )
                if not existing.image and bean.image:
                    existing.image = bean.image
            else:
                bean.name = normalized_name
                all_beans_by_key[key] = bean

        next_url = _find_next_page_url(html)
        if not next_url or next_url == url:
            break
        url = next_url

    return list(all_beans_by_key.values())


if __name__ == "__main__":
    beans = asyncio.run(scrape_yume_store())
    for bean in beans:
        print(bean)
