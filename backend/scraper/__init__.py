from scraper.embuStore import scrape_embu_store

# Map DB store.name -> scraper function
SCRAPERS = {
    "Embu": scrape_embu_store
}

