import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

    
def scrape_dynamic_data(max_patches: int) -> dict:

    url = "https://robertsspaceindustries.com/spectrum/community/SC/forum/190048?sort=hot&page=1"
    
    service = Service('./chromedriver')
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
        
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "row.thread"))
        )
        print("LOG: Haupt-Container gefunden. Starte Extraktion.")
        
        thread_rows = driver.find_elements(By.CLASS_NAME, "row.thread")
        
        if not thread_rows:
             return {"error": "Keine Thread-Zeilen ('row thread') auf der Seite gefunden."}
        
        print(f"LOG: Gefundene Threads: {len(thread_rows)}")

        for row in thread_rows:
            if len(results) >= max_patches:
                print(f"LOG: Limit von {max_patches} Elementen erreicht. Beende Schleife.")
                break
            try:
                subject_element = row.find_element(By.CLASS_NAME, "thread-subject")
                subject_text = subject_element.text.strip()
                subject_href = subject_element.get_attribute('href')
                
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

        return {"threads": results}

    except Exception as e:
        print(f"Ein Fehler beim Scraping ist aufgetreten: {e}")
        return {"error": str(e)}

    finally:
        driver.quit()
        print("Browser geschlossen.")
