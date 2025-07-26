from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Optional

from ..scraper.embuStore import scrape_embu_store
from ..utils import flatten_variants, fetch_cached_beans
from ..cache import set_cached_beans, get_last_updated

router = APIRouter()


@router.get("/beans")
# Scrapes all stores for coffee beans
def fetch_beans(
        store: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = Query(None, enum=["price", "price_per_gram", "name"],
                                       description="Sort by 'price' or 'price_per_gram' or alphabetical")
):
    beans = fetch_cached_beans()
    if store:
        beans = [bean for bean in beans if bean.store.lower() == store.lower()]
    if min_price:
        beans = [bean for bean in beans if any(v.price >= min_price for v in bean.variants)]
    if max_price:
        beans = [bean for bean in beans if any(v.price <= max_price for v in bean.variants)]
    match sort_by:
        case "price":
            beans.sort(key=lambda x: min(v.price for v in x.variants))
        case "price_per_gram":
            beans.sort(key=lambda x: min(v.price_per_gram for v in x.variants))
        case "name":
            beans.sort(key=lambda x: x.name.lower())
    response = {
        "last_updated": get_last_updated(),
        "beans": beans,
        "count": len(beans)
    }
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/leaderboard")
# Returns a leaderboard of coffee beans based on price per gram, can use filters
def leaderboard(
        grams: Optional[List[int]] = Query(None),
        top: int = 10
):
    beans = fetch_cached_beans()
    lb_entries = flatten_variants(beans, grams_filter=grams)
    lb_entries.sort(key=lambda x: x.price_per_gram)
    lb_entries = lb_entries[:top]
    response = {
        "last_updated": get_last_updated(),
        "entries": lb_entries,
        "top": top
    }
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/refresh")

def refresh_cache():
    beans= scrape_embu_store()
    set_cached_beans(beans)
    return JSONResponse({
        "message": "Cache refreshed successfully",
        "timestamp":get_last_updated()
    })
