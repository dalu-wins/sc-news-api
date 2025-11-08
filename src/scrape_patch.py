import base64
import json
import os
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import LOCK_FILE, LOCK_TIMEOUT_MINUTES, WAIT_FOR_LOCK_TIMEOUT, WAIT_FOR_LOCK_INTERVAL, CHROMEDRIVER, PATCH_CACHE_DIR, PATCH_CACHE_MAX_AGE_MINUTES

app = FastAPI(title="Patchnotes API")

# === Lock-Handling ===
def is_scrape_running() -> bool:
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        lock_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOCK_FILE))
        if lock_age > timedelta(minutes=LOCK_TIMEOUT_MINUTES):
            os.remove(LOCK_FILE)
            return False
        return True
    except Exception:
        return False


def set_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(datetime.now()))


def clear_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception as e:
        print(f"WARNUNG: Lock konnte nicht gelöscht werden: {e}")


# === Scraper ===
def scrape_notes(url_b64: str) -> dict:
    driver = None
    try:
        os.makedirs(PATCH_CACHE_DIR, exist_ok=True)
        cachefile = os.path.join(PATCH_CACHE_DIR, url_b64 + ".json")

        # Cache prüfen
        if os.path.exists(cachefile):
            with open(cachefile, "r", encoding="utf-8") as f:
                data = json.load(f)
            age = datetime.now() - datetime.fromisoformat(data["timestamp"])
            if age < timedelta(minutes=PATCH_CACHE_MAX_AGE_MINUTES):
                data["status"] = "cached"
                return data

        # Warten falls Lock aktiv
        waited = 0
        while is_scrape_running():
            if waited >= WAIT_FOR_LOCK_TIMEOUT:
                if os.path.exists(cachefile):
                    with open(cachefile, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data["status"] = "waiting"
                    return data
                return {"status": "waiting", "sections": {}}
            time.sleep(WAIT_FOR_LOCK_INTERVAL)
            waited += WAIT_FOR_LOCK_INTERVAL

        set_lock()

        # URL dekodieren
        url = base64.b64decode(url_b64).decode("utf-8")

        # Selenium Setup
        service = Service(CHROMEDRIVER)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        wait = WebDriverWait(driver, 15)
        content_div = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-block.text"))
        )

        html = content_div.get_attribute("outerHTML")

        # === HTML analysieren ===
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_="content-block text")
        sections = {}
        current_title = None

        for element in container.find_all(recursive=False):
            if element.name == "h1":
                current_title = element.get_text(strip=True)
                # Duplikate vermeiden
                if current_title in sections:
                    i = 2
                    base_title = current_title
                    while f"{base_title} ({i})" in sections:
                        i += 1
                    current_title = f"{base_title} ({i})"
                sections[current_title] = []
            elif current_title and element.name:
                sections[current_title].append(str(element))

        # Sections als HTML zurückgeben
        sections_html = {title: "".join(elements) for title, elements in sections.items()}

        data = {
            "timestamp": datetime.now().isoformat(),
            "status": "fresh",
            "url": url,
            "notes": sections_html
        }

        # Cache speichern
        with open(cachefile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data

    except Exception as e:
        print(f"Ein Fehler beim Scraping ist aufgetreten: {e}")
        err = {"status": "error", "error": str(e)}
        return err
    finally:
        if driver:
            driver.quit()
        clear_lock()