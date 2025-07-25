from backend.scraper.embuStore import scrape_embu_store

def test_scrape_embu_store():
    beans=scrape_embu_store()
    print(f"Found {len(beans)} coffee bean products:")
    for bean in beans:
        print(bean.json())

if __name__ == "__main__":
    test_scrape_embu_store()