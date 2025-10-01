import asyncio, httpx

async def get_response(url):
    async with httpx.AsyncClient() as client:
        response=await client.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return None
    return response.text