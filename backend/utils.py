from models import CoffeeBean, LeaderboardEntry
from typing import List, Optional
from cache import get_cached_beans, set_cached_beans
from scraper.embuStore import scrape_embu_store

# Utility function to flatten coffee bean variants into leaderboard entries
def flatten_variants(
    beans: List[CoffeeBean],
    grams_filter: Optional[List[int]] = None
) -> List[LeaderboardEntry]:
    flattened = []
    for bean in beans:
        for v in bean.variants:
            if grams_filter is None or v.grams in grams_filter:
                flattened.append(LeaderboardEntry(
                    name=bean.name,
                    store=bean.store,
                    url=bean.url,
                    image=bean.image,
                    grams=v.grams,
                    price=v.price,
                    price_per_gram=v.price_per_gram
                ))
    return flattened

# Function to fetch cached coffee beans
def fetch_cached_beans()->List[CoffeeBean]:
    beans=get_cached_beans()
    if not beans:
        beans = scrape_embu_store()
        set_cached_beans(beans)
    return beans