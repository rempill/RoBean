import logging
from urllib.parse import urlparse
from curl_cffi.requests import AsyncSession

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
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
    try:
        async with AsyncSession(impersonate="chrome") as session:
            response = await session.get(url, headers=req_headers, timeout=20, follow_redirects=True)
            if response.status_code != 200:
                logger.warning(f"HTTP error {response.status_code} for URL: {url}")
                return None
            return response.text
    except Exception as e:
        logger.error(f"Network error fetching URL {url}: {e}")
        return None
