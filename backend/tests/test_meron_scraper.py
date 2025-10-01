from unittest.mock import AsyncMock, patch
import asyncio
from scraper import SCRAPERS
import logging
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

# Mock response
class MockResponse:
    def __init__(self, text):
        self.text = text
        self.status_code = 200

async def get_side_effect(url,*args, **kwargs):
    if url.endswith("/categorie-produs/cafea/"):
        with open("backend/tests/fixtures/meron.html") as f:
            return MockResponse(f.read())
    elif "best-of-panama-box" in url:
        with open("backend/tests/fixtures/meron_box.html") as f:
            return MockResponse(f.read())
    return MockResponse("")

@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_scrape_meron_store(mock_get):
    mock_get.side_effect=get_side_effect
    beans=asyncio.run(SCRAPERS["Meron"]())

    assert len(beans)==4
    bean_names=[bean.name for bean in beans]
    assert "Best of Panama – Box" in bean_names
    assert "Brazil Sarava" in bean_names
    assert "Kune - House Blend" in bean_names
    assert "Kune - Brazilia" in bean_names
    assert "Meron Card" not in bean_names
    for bean in beans:
        if bean.name=="Best of Panama – Box":
            assert len(bean.variants)==1
            first_variant=bean.variants[0]
            assert first_variant.grams==240
            assert first_variant.price==380.0
            assert first_variant.price_per_gram==1.583
        elif bean.name=="Brazil Sarava":
            assert len(bean.variants)==2
            variant_1kg=next((v for v in bean.variants if v.grams==1000), None)
            assert variant_1kg is not None
            assert variant_1kg.price==189.0
            assert variant_1kg.price_per_gram==0.189
        elif bean.name=="Kune - House Blend":
            assert len(bean.variants)==3
            variant_250g=next((v for v in bean.variants if v.grams==250), None)
            assert variant_250g is not None
            assert variant_250g.price==52.0
            assert variant_250g.price_per_gram==0.208
        elif bean.name=="Kune - Brazilia":
            assert len(bean.variants)==1
            variant_250g=next((v for v in bean.variants if v.grams==250), None)
            assert variant_250g is not None
            assert variant_250g.price==51.0
            assert variant_250g.price_per_gram==0.204