from fastapi import FastAPI
from scrape_overview import scrape_overview
from scrape_patch import scrape_notes
from subject_parser import parse_patch_entry
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

from config import LOCK_FILE, LOCK_TIMEOUT_MINUTES

import base64
import os

app = FastAPI()

# needed for status on website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.dalu-wins.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/patch-notes/all")
def get_scraped_overview(max_patches: int = 50):
    scraped_data = scrape_overview(max_patches=max_patches)

    if scraped_data.get("error"):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data["error"]}, 500

    parsed_patches = [parse_patch_entry(t) for t in scraped_data.get("threads", [])]

    latest_per_channel = {}
    for patch in parsed_patches:
        if patch["pinned"]:
            ch = patch["channel"]
            if ch not in latest_per_channel:
                latest_per_channel[ch] = patch

    for patch in parsed_patches:
        patch["currently_online"] = (latest_per_channel.get(patch["channel"]) == patch)

    return {
        "status": "success",
        "data": {
            "timestamp": scraped_data.get("timestamp"),
            "cacheStatus": scraped_data.get("status"),
            "patches": parsed_patches,
        },
    }

@app.get("/patch-notes/thread")
def get_scraped_note(url_base64: str):

    scraped_data = scrape_notes(url_b64=url_base64)

    if scraped_data.get("error"):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data["error"]}, 500

    return {
        "status": "success",
        "data": {
            "timestamp": scraped_data.get("timestamp"),
            "cacheStatus": scraped_data.get("status"),
            "url": scraped_data.get("url"),
            "notes": scraped_data.get("notes", []),
        }
    }

def is_scrape_running() -> bool:
    """Checkt, ob die Lockdatei existiert und noch gültig ist."""
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        lock_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOCK_FILE))
        if lock_age > timedelta(minutes=LOCK_TIMEOUT_MINUTES):
            # Alte Lockdatei — gilt als abgelaufen
            return False
        return True
    except Exception:
        return False

@app.get("/patch-notes/status")
def get_status():
    if is_scrape_running():
        return {"status": "active"}
    return {"status": "idle"}