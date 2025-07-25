from fastapi import FastAPI
from tests.backend.shortScraper import test_scrape_embu_store

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

test_scrape_embu_store()
