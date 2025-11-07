from fastapi import FastAPI
from scrape_overview import scrape_overview
from scrape_patch import scrape_notes
from subject_parser import parse_patch_entry

import base64

app = FastAPI()

@app.get("/patch-notes/all")
def get_scraped_overview(max_patches: int = 50):
    scraped_data = scrape_overview(max_patches=max_patches)

    if scraped_data.get("error"):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data["error"]}, 500

    parsed_patches = [parse_patch_entry(t) for t in scraped_data.get("threads", [])]

    return {
        "status": "success",
        "data": {
            "timestamp": scraped_data.get("timestamp"),
            "cacheStatus": scraped_data.get("status"),
            "patches": parsed_patches,
        },
    }

@app.get("/patch-notes/thread")
def get_scraped_note(url_b64: str):

    scraped_data = scrape_notes(url_b64=url_b64)

    if scraped_data.get("error"):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data["error"]}, 500

    return {
        "status": "success",
        "data": {
            "timestamp": scraped_data.get("timestamp"),
            "cacheStatus": scraped_data.get("status"),
            "notes": scraped_data.get("notes", []),
        }
    }