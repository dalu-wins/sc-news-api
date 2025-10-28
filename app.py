from fastapi import FastAPI
from scraper import scrape_dynamic_data


app = FastAPI()

@app.get("/api/patches")
def get_scraped_info(max_patches: int = 50):
       
    scraped_data = scrape_dynamic_data(max_patches = max_patches)
    
    if scraped_data.get('error'):
        return {"status": "failure", "message": "Scraping fehlgeschlagen", "details": scraped_data['error']}, 500
        
    return {"status": "success", "data": scraped_data}
