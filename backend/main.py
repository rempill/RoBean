from fastapi import FastAPI

from tests.backend.shortScraper import test_scrape_embu_store
from backend.api.beans import router as beans_router

app = FastAPI()
app.include_router(beans_router,prefix="/beans")

test_scrape_embu_store()
