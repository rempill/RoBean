from unittest.mock import AsyncMock, patch
import asyncio

from scraper import SCRAPERS


class MockResponse:
    def __init__(self, text: str):
        self.text = text
        self.status_code = 200


async def get_side_effect(url, *args, **kwargs):
    # The scraper starts at https://yume.coffee/en_US/shop
    if url == "https://yume.coffee/en_US/shop":
        with open("backend/tests/fixtures/yume_shop_page1.html", "r", encoding="utf-8") as f:
            return MockResponse(f.read())

    if url == "https://yume.coffee/en_US/shop?page=2":
        with open("backend/tests/fixtures/yume_shop_page2.html", "r", encoding="utf-8") as f:
            return MockResponse(f.read())

    return MockResponse("")


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_scrape_yume_store(mock_get):
    mock_get.side_effect = get_side_effect

    beans = asyncio.run(SCRAPERS["Yume"]())

    assert len(beans) == 2

    # Grouped variants under one normalized bean
    guji = next((b for b in beans if b.name == "Ethiopia Guji"), None)
    assert guji is not None
    assert len(guji.variants) == 2

    v250 = next((v for v in guji.variants if v.grams == 250), None)
    assert v250 is not None
    assert v250.price == 58.0
    assert v250.price_per_gram == 0.232

    v1kg = next((v for v in guji.variants if v.grams == 1000), None)
    assert v1kg is not None
    assert v1kg.price == 180.0
    assert v1kg.price_per_gram == 0.18

    flores = next((b for b in beans if b.name == "Colombia Las Flores"), None)
    assert flores is not None
    assert len(flores.variants) == 1
    assert flores.variants[0].grams == 250
    assert flores.variants[0].price == 77.0
    assert flores.variants[0].price_per_gram == 0.308

