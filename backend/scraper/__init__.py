from .embu_store import scrape_embu_store
from .meron_store import scrape_meron_store
from .yume_store import scrape_yume_store

# Map DB store.name -> scraper function
SCRAPERS = {
    "Embu": scrape_embu_store,
    "Meron": scrape_meron_store,
    "Yume": scrape_yume_store,
}
