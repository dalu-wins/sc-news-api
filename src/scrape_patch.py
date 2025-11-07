import base64
import json
import os
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# === Konfiguration ===
CACHE_DIR = "./cache/notes/"
LOCK_FILE = ".scrape.lock"
CHROMEDRIVER = "/usr/bin/chromedriver"
CACHE_MAX_AGE_MINUTES = 10
LOCK_TIMEOUT_MINUTES = 5
WAIT_FOR_LOCK_TIMEOUT = 60  # max. 60 Sekunden warten
WAIT_FOR_LOCK_INTERVAL = 2  # Prüfintervall


# === Lock-Handling ===
def is_scrape_running() -> bool:
    """Prüft, ob ein anderer Scrape läuft."""
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        lock_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOCK_FILE))
        if lock_age > timedelta(minutes=LOCK_TIMEOUT_MINUTES):
            print("WARNUNG: Alte Lockdatei erkannt – entferne sie.")
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


# === Hauptfunktion ===
def scrape_notes(url_b64: str) -> dict:
    """Scraped Patchnotes (content-block text) mit Cache und Lock-System."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cachefile = os.path.join(CACHE_DIR, url_b64 + ".json")

    # Cache prüfen
    if os.path.exists(cachefile):
        with open(cachefile, "r", encoding="utf-8") as f:
            data = json.load(f)
        age = datetime.now() - datetime.fromisoformat(data["timestamp"])
        if age < timedelta(minutes=CACHE_MAX_AGE_MINUTES):
            print("LOG: Cache ist aktuell – verwende gespeicherte Daten.")
            data["status"] = "cached"
            return data
        else:
            print("LOG: Cache ist veraltet – lade neu.")

    # Wenn gerade ein anderer Scrape läuft, warten
    waited = 0
    while is_scrape_running():
        if waited >= WAIT_FOR_LOCK_TIMEOUT:
            print("WARNUNG: Timeout beim Warten auf Lock – gebe evtl. alten Cache zurück.")
            if os.path.exists(cachefile):
                with open(cachefile, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["status"] = "waiting"
                return data
            return {"status": "waiting", "sections": {}}
        print(f"LOG: Warte {waited}s auf Lock-Freigabe...")
        time.sleep(WAIT_FOR_LOCK_INTERVAL)
        waited += WAIT_FOR_LOCK_INTERVAL

    # Lock setzen
    set_lock()

    # URL dekodieren
    url = base64.b64decode(url_b64).decode("utf-8")
    print(f"LOG: Lade Seite: {url}")

    # Selenium Setup
    service = Service(CHROMEDRIVER)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        content_div = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-block.text"))
        )
        print("LOG: content-block gefunden.")

        html = content_div.get_attribute("outerHTML")
        text = content_div.text.strip()

        # === HTML analysieren ===
        soup = BeautifulSoup(html, "html.parser")

        container = soup.find("div", class_="content-block text")
        sections = {}
        current_title = None 

        print("DEBUG: Starte Section-Parsing...")

        for element in container.find_all(recursive=False):  # nur direkte Kinder des Containers
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
                print(f"DEBUG: Neue Section: '{current_title}'")
            elif element.name and current_title:
                sections[current_title].append(str(element))
                print(f"DEBUG: Element zu Section '{current_title}' hinzugefügt, aktuell {len(sections[current_title])} Elemente")
            else:
                print(f"DEBUG: Element übersprungen (kein aktueller Section-Title): {element.name}")
                
        print("\nDEBUG: Fertig mit Section-Parsing.")
        print(f"DEBUG: Gesamtzahl der Sections: {len(sections)}")
        for title, elems in sections.items():
            print(f"  - Section '{title}': {len(elems)} Elemente")


        sections_text = {}
        for title, contents in sections.items():
            section_html = "".join(contents)
            section_soup = BeautifulSoup(section_html, "html.parser")
            lines = [line for line in section_soup.get_text("\n", strip=True).split("\n") if line.strip()]
            sections_text[title] = lines

        data = {
            "status": "fresh",
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "html": html,
            "text": text,
            "sections": sections_text,
        }

        with open(cachefile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"LOG: Cache aktualisiert ({len(sections)} Abschnitte).")
        return data

    except Exception as e:
        print(f"FEHLER beim Scrapen: {e}")
        return {"status": "error", "error": str(e)}

    finally:
        driver.quit()
        clear_lock()
        print("Browser geschlossen, Lock entfernt.")
