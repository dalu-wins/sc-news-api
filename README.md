# <img src="https://github.com/dalu-wins/sc-news/blob/main/assets/app_icon.svg" alt="App Icon" height="32"> Star Citizen News API
Provide information to the [SC-News](https://github.com/dalu-wins/sc-news) app.

## 📝 Variables
| Variable | Description |
--- | ---
max_patches | Set the limit of patches that the api will return

## 🗄️ Public API

A public API is hosted on my server:
- [https://sc-news.api.dalu-wins.de/](https://sc-news.api.dalu-wins.de/)

> ⚠️ While the API should handle concurrent access safely, please **avoid unnecessary request spamming** to keep the service stable.

## 🛠️ Setup

For an easy setup, use Docker Compose.  

### Steps

By default, the API container exposes port 8000.

```bash
# Clone the repository
git clone https://github.com/dalu-wins/sc-news-api.git

# Go into the project folder
cd sc-news-api

# Build and start the API container in detached mode
docker compose up --build -d
```

> Note: Android requires HTTPS to access the API.

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
