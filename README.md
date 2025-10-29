# <img src="https://github.com/dalu-wins/sc-news/blob/main/assets/app_icon.svg" alt="App Icon" height="32"> Star Citizen News API
Provide information to the SC News app.

## 📝 Endpoints
Endpoint | Variables | Description |
--- | --- | ---
`/api/patches` | max_patches | Set the limit of patches that the api will return 

## 🛠️ Setup

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

Now you should be able to check if the api is correctly running with ```http://localhost:8000/api/patches?max_patches=10```
