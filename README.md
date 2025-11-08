# Star Citizen News API
Retrieves the latest Star Citizen news for the [SC-News](https://github.com/dalu-wins/sc-news) app.

## 🗄️ Public API
**Hosted on:** [https://www.dalu-wins.de/](https://www.dalu-wins.de/)<br>
**Subdomain:** [https://sc-news.api.dalu-wins.de/](https://sc-news.api.dalu-wins.de/)

> Note: While the API should handle concurrent access safely, please **avoid unnecessary request spamming** to keep the service stable.

## 🛠️ Setup

If you want to host the API yourself, you can use Docker Compose to set it up.

Edit the `docker-compose.yml` to your needs. By default, the API container runs on port 8000.

```bash
# Clone the repository
git clone https://github.com/dalu-wins/sc-news-api.git
cd sc-news-api

# Build and start the API container in detached mode
docker compose up --build -d
```

> Note: Android requires HTTPS to access the API.


## 📝 Endpoints & Parameters

| Endpoint | Parameters | Description |
|----------|------------|-------------|
| `/patch-notes/all` | `max_patches` – optional  | An overview of all patch notes |
| `/patch-notes/thread` | `url_base64` – mandatory | Details of a specific patch |
| `/patch-notes/status` | – | If the scraper is currently idle or active |

> Note: The Base64 encoding of a patch url is included in the result of `/patch-notes/all`

## ℹ️ Notice & Disclaimers

This is an unofficial Star Citizen fan project, not affiliated with the Cloud Imperium group of
companies. All content provided by this api not authored by its developers or users are property of their
respective owners.

Star Citizen®, Roberts Space Industries® and Cloud Imperium ® are registered trademarks of Cloud
Imperium Rights LLC

<p align="center">
  <img src="https://github.com/dalu-wins/sc-news/blob/main/assets/MadeByTheCommunity_White.png" alt="Made By The Community Banner" height="200">
  <img height="200" src="https://github.com/dalu-wins/sc-news/blob/main/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.webp">
</p>
