# CollectPosts - Social Media Scraping API

A modular FastAPI service for collecting posts from Reddit, YouTube, Instagram, and Quora.

## 🏗️ Project Structure

```
collectPosts/
├── main.py                 # Main entry point
├── client.py              # Client access point
├── scraper.py             # Main scraper coordinator
├── scrapers/              # Platform-specific scrapers
│   ├── __init__.py
│   ├── reddit_scraper.py
│   ├── youtube_scraper.py
│   ├── instagram_scraper.py
│   └── quora_scraper.py
├── api/                   # API components
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   └── client_package.py # API client
├── docs/                  # Documentation
│   ├── README.md
│   └── CLIENT_README.md
├── requirements.txt
├── render.yaml
├── Procfile
└── runtime.txt
```

## 🚀 Quick Start

### Running the API Server
```bash
python main.py
```

### Using the Client
```python
from client import api

# Scrape posts
data, status = api(subreddit='politics', limit=10, time_passed='week')
print(data.head())
```

## 📊 Features

- **Multi-platform scraping**: Reddit, YouTube, Instagram, Quora
- **Time filtering**: day, week, month, year
- **Modular architecture**: Easy to extend and maintain
- **REST API**: Deploy on Render, Heroku, etc.
- **Client package**: Simple Python interface

## 🔧 Configuration

Set environment variables:
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`
- `YOUTUBE_API_KEY`
- `INSTAGRAM_USERNAME` / `INSTAGRAM_PASSWORD`

## 📚 Documentation

See `docs/` folder for detailed documentation.
