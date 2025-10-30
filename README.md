# <img src="https://github.com/dalu-wins/sc-news/blob/main/assets/app_icon.svg" alt="App Icon" height="32"> Star Citizen SC-News API
Provide information to the [SC-News](https://github.com/dalu-wins/sc-news) app.

## 📝 Variables
| Variable | Description |
--- | ---
max_patches | Set the limit of patches that the api will return

## 🗄️ Server
The public API is hosted on my homepage:
- [https://www.dalu-wins.de/](https://www.dalu-wins.de/)
- [https://api.dalu-wins.de/sc-news](https://api.dalu-wins.de/sc-news)

The API implements caching and concurrency protection:
- Scraped results are cached for **5 minutes**.
- Only **one scraping job** can run at a time.
- If multiple clients call the API simultaneously, subsequent requests **wait** for the first scrape to finish and then **read from the cache**.
- This means that **at most one scrape per 10 minutes** is performed, minimizing load on Spectrum.

While the API should handle concurrent access safely, please **avoid unnecessary request spamming** to keep the service stable.

## 🛠️ Setup
Make sure you have installed `python3` beforehand. You might need to run the python steps fromS `venv`.

### Clone repo & install requirements
```bash
# Clone
git clone https://github.com/dalu-wins/sc-news-api.git

# Install python requirements
cd sc-news-api/src
pip install -r requirements.txt
```

### Install Chromium, wget, unzip
```bash
# Update if necessary
sudo apt update

# Install requirements
sudo apt install chromium -y
sudo apt install wget -y
sudo apt install unzip -y
```

### Download, unzip & place Chrome Driver in repo's root directory
```bash
# Important: Match Chrome Driver version with your chromium version!
wget https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.122/linux64/chromedriver-linux64.zip

# Unzip, move & make executable
unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver .
chmod +x chromedriver

# Remove unnecessary files
rm -rf chromedriver-linux64 chromedriver-linux64.zip
```

### Start server
```bash
# Adjust host and port if needed
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Now you should be able to check if the api is correctly running with ```http://localhost:8000?max_patches=10```

## ✍ Documentation

Learn more about this project:
- [Project Board](https://github.com/users/dalu-wins/projects/3/views/1)
- [SC News App](https://github.com/dalu-wins/sc-news)

## ℹ️ Notice & Disclaimers

This is an unofficial Star Citizen fan project, not affiliated with the Cloud Imperium group of
companies. All content provided by this api not authored by its developers or users are property of their
respective owners.

Star Citizen®, Roberts Space Industries® and Cloud Imperium ® are registered trademarks of Cloud
Imperium Rights LLC

<p align="center">
  <img src="https://github.com/dalu-wins/sc-news/blob/main/assets/MadeByTheCommunity_White.png" alt="Made By The Community Banner" height="200">
</p>
