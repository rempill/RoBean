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
    if url.endswith("per_page=100"):
        with open("backend/tests/fixtures/meron_products.json", "r", encoding="utf-8") as f:
            return MockResponse(f.read())
    return MockResponse("")

@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_scrape_meron_store(mock_get):
    mock_get.side_effect=get_side_effect
    beans=asyncio.run(SCRAPERS["Meron"]())

    assert len(beans)==4
    bean_names=[bean.name for bean in beans]
    assert "Colombia Las Flores" in bean_names
    assert "Colombia Rodrigo Sanchez" in bean_names
    assert "Kune Colombia" in bean_names
    assert "Kune Blend" in bean_names
    assert "Kune House Blend" not in bean_names
    assert "Meron Online Gift Card" not in bean_names
    assert "Best of Panama Box" not in bean_names
    for bean in beans:
        match bean.name:
            case "Colombia Las Flores":
                assert len(bean.variants)==2
                variant_250g=next((v for v in bean.variants if v.grams==250), None)
                assert variant_250g is not None
                assert variant_250g.price==77.0
                assert variant_250g.price_per_gram==0.308
                assert str(bean.url)=="https://meron.ro/?s=Colombia+Las+Flores&post_type=product"
            case "Colombia Rodrigo Sanchez":
                assert len(bean.variants)==1
                only_variant=bean.variants[0]
                assert only_variant.grams==250
                assert only_variant.price==100.0
                assert only_variant.price_per_gram==0.4
                assert str(bean.url)=="https://meron.ro/produs/colombia-rodrigo-sanchez-250g-bourbon-sidra-spalata/"
            case "Kune Colombia":
                assert len(bean.variants)==3
                variant_500g=next((v for v in bean.variants if v.grams==500), None)
                assert variant_500g is not None
                assert variant_500g.price==99.0
                assert variant_500g.price_per_gram==0.198
                assert str(bean.url)=="https://meron.ro/?s=Kune+Colombia&post_type=product"
            case "Kune Blend":
                assert len(bean.variants)==2
                variant_1kg=next((v for v in bean.variants if v.grams==1000), None)
                assert variant_1kg is not None
                assert variant_1kg.price==180.0
                assert variant_1kg.price_per_gram==0.18
                assert str(bean.url)=="https://meron.ro/?s=Kune+Blend&post_type=product"
            case _:
                assert False, f"Unexpected bean name: {bean.name}"