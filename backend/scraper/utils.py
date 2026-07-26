import asyncio
from urllib.parse import urlparse
import httpx

DEFAULT_HEADERS = {
    # 1. Stops Python from identifying itself as a bot
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    # 2. Tells Shopify/WP you want JSON, not an HTML page
    "Accept": "application/json, text/plain, */*",
}


def get_headers_for_url(url: str, custom_headers: dict | None = None) -> dict:
    parsed = urlparse(url)
    referer = f"{parsed.scheme}://{parsed.netloc}/" if parsed.netloc else url
    headers = {
        **DEFAULT_HEADERS,
        "Referer": referer,
    }
    if custom_headers:
        headers.update(custom_headers)
    return headers


async def get_response(url: str, headers: dict | None = None) -> str | None:
    req_headers = get_headers_for_url(url, headers)
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(url, headers=req_headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return None
    return response.text