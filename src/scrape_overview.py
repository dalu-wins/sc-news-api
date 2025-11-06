import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# === Konfiguration ===
CACHE_FILE = "./cache/spectrum_cache.json"
LOCK_FILE = ".scrape.lock"
CHROMEDRIVER = "/usr/bin/chromedriver"
CACHE_MAX_AGE_MINUTES = 5
LOCK_TIMEOUT_MINUTES = 5
WAIT_FOR_LOCK_TIMEOUT = 60  # maximal 60 Sekunden warten
WAIT_FOR_LOCK_INTERVAL = 2  # alle 2 Sekunden prüfen


# === Hilfsfunktionen ===
def load_cache():
    """Lädt den Cache, wenn vorhanden."""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        timestamp = datetime.fromisoformat(data.get("timestamp"))
        age = datetime.now() - timestamp
        if age < timedelta(minutes=CACHE_MAX_AGE_MINUTES):
            print("LOG: Cache ist gültig.")
            data["status"] = "cached"
        else:
            print(f"LOG: Cache ist {age.total_seconds() / 60:.1f} Minuten alt (veraltet).")
            data["status"] = "stale"
        return data
    except Exception as e:
        print(f"WARNUNG: Cache konnte nicht geladen werden: {e}")
        return None


def save_cache(data: dict):
    """Speichert den Cache mit aktuellem Timestamp."""
    data["timestamp"] = datetime.now().isoformat()
    data["status"] = "fresh"
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("LOG: Cache aktualisiert.")
    except Exception as e:
        print(f"WARNUNG: Cache konnte nicht gespeichert werden: {e}")


def is_scrape_running() -> bool:
    """Prüft, ob aktuell ein Scrape läuft."""
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        lock_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOCK_FILE))
        if lock_age > timedelta(minutes=LOCK_TIMEOUT_MINUTES):
            print("WARNUNG: Alte Lockdatei erkannt — entferne sie.")
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


def limit_cache(data: dict, max_patches: int) -> dict:
    """Begrenzt die Anzahl der Einträge für den Rückgabewert."""
    threads = data.get("threads", [])
    limited = threads[:max_patches] if max_patches > 0 else threads
    return {
        "timestamp": data.get("timestamp"),
        "status": data.get("status"),
        "threads": limited
    }


# === Hauptlogik ===
def scrape_overview(max_patches: int) -> dict:
    """Scraped Threads, nutzt Cache und Lock-System."""
    cached = load_cache()
    # Frischen Cache direkt zurückgeben
    if cached and cached.get("status") == "cached":
        return limit_cache(cached, max_patches)
    # Wenn gerade ein anderer Scrape läuft → warten
    if is_scrape_running():
        print("LOG: Ein anderer Scrape läuft — warte auf Freigabe...")
        waited = 0
        while is_scrape_running() and waited < WAIT_FOR_LOCK_TIMEOUT:
            time.sleep(WAIT_FOR_LOCK_INTERVAL)
            waited += WAIT_FOR_LOCK_INTERVAL
            print(f"LOG: Warte {waited}s auf Lock-Freigabe...")
        # Nach Warten: prüfen, ob Cache aktualisiert wurde
        if is_scrape_running():
            print("WARNUNG: Lock nach Timeout immer noch aktiv — gebe alten Cache zurück.")
            if cached:
                cached["status"] = "waiting"
                return limit_cache(cached, max_patches)
            return {"status": "waiting", "threads": []}
        print("LOG: Lock wurde freigegeben — lade neuen Cache.")
        new_cache = load_cache()
        if new_cache:
            return limit_cache(new_cache, max_patches)
        else:
            print("WARNUNG: Kein neuer Cache nach Freigabe — starte Scrape trotzdem.")
    # Lock setzen, um parallele Scrapes zu verhindern
    set_lock()
    url = "https://robertsspaceindustries.com/spectrum/community/SC/forum/190048?sort=hot&page=1"
    service = Service(CHROMEDRIVER)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    results = []
    try:
        driver.get(url)
        print(f"LOG: Navigiert zu: {url}")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "row.thread")))
        print("LOG: Haupt-Container gefunden. Starte Extraktion.")
        thread_rows = driver.find_elements(By.CLASS_NAME, "row.thread")
        print(f"LOG: Gefundene Threads: {len(thread_rows)}")
        for row in thread_rows:
            try:
                subject_element = row.find_element(By.CLASS_NAME, "thread-subject")
                subject_text = subject_element.text.strip()
                subject_href = subject_element.get_attribute("href")
                is_pinned = False
                try:
                    row.find_element(By.CSS_SELECTOR, "span.thread-flag.thread-flag-label.pinned")
                    is_pinned = True
                except Exception:
                    pass
                results.append({
                    "subject": subject_text,
                    "url": subject_href,
                    "pinned": is_pinned,
                })
            except Exception as e:
                print(f"WARNUNG: Konnte Zeile nicht parsen: {e}")
                continue
        result_data = {"threads": results}
        save_cache(result_data)
        result_data["status"] = "fresh"
        return limit_cache(result_data, max_patches)
    except Exception as e:
        print(f"Ein Fehler beim Scraping ist aufgetreten: {e}")
        err = {"status": "error", "error": str(e), "threads": []}
        return err
    finally:
        driver.quit()
        clear_lock()
        print("Browser geschlossen, Lock entfernt.")
