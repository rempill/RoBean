from unittest.mock import AsyncMock, patch
import asyncio
from scraper import SCRAPERS


# Mock response
class MockResponse:
    def __init__(self, text):
        self.text = text
        self.status_code = 200


async def get_side_effect(url, *args, **kwargs):
    if url.endswith("products.json"):
        with open("backend/tests/fixtures/embu_products.json", "r", encoding="utf-8") as f:
            return MockResponse(f.read())

    return MockResponse("")


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_scrape_embu_store(mock_get):
    mock_get.side_effect = get_side_effect
    beans = asyncio.run(SCRAPERS["Embu"]())

    assert len(beans) == 2
    bean_names = [bean.name for bean in beans]
    assert "Brazilia F1" in bean_names
    assert "Ethiopia Guji" in bean_names

    for bean in beans:
        if bean.name == "Brazilia F1":
            assert len(bean.variants) == 2
            variant_250g = next((v for v in bean.variants if v.grams == 250), None)
            assert variant_250g is not None
            assert variant_250g.price == 52.0
            assert variant_250g.price_per_gram == 0.208
        elif bean.name == "Ethiopia Guji":
            assert len(bean.variants) == 2
            variant_1kg = next((v for v in bean.variants if v.grams == 1000), None)
            assert variant_1kg is not None
            assert variant_1kg.price == 210.0
            assert variant_1kg.price_per_gram == 0.21
