from fastapi import FastAPI
from scraper import scrape_dynamic_data
from parser import parse_patch_entry

app = FastAPI()

@app.get("/")
def get_scraped_info(max_patches: int = 50):
    scraped_data = scrape_dynamic_data(max_patches=max_patches)

    if scraped_data.get("error"):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data["error"]}, 500

    # Threads in Patches umwandeln
    parsed_patches = [parse_patch_entry(t) for t in scraped_data.get("threads", [])]

    return {
        "status": "success",
        "data": {
            "timestamp": scraped_data.get("timestamp"),
            "cacheStatus": scraped_data.get("status"),
            "patches": parsed_patches,
        },
    }
