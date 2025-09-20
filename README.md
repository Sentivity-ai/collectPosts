# CollectPosts API

A simple social media scraping API that collects posts from Reddit, YouTube, and Instagram.

## Quick Start

### For Users (Client Package)

```python
from client_package import api

# Get posts directly into your script
data, status = api(subreddit="labubu", limit="100", time_passed="week")

# Data is now in 'data' variable as DataFrame
print(f"Got {len(data)} posts")
print(data.head())
```

### Installation

```bash
pip install requests pandas
```

## API Usage

```python
# Your exact example
data = api(subreddit="labubu", limit="100", time_passed="week")

# General topic search
data = api(query="technology", limit=50)

# Specific sources only
data = api(query="AI", sources=["reddit", "youtube"], limit=100)

# Different time periods
data = api(subreddit="politics", time_passed="month", limit=200)
```

## What You Get

**DataFrame with columns:**
- `title`: Post title/content
- `content`: Full post text
- `author`: Username/creator
- `score`: Engagement metrics
- `url`: Link to post
- `timestamp`: When posted
- `source`: reddit/youtube/instagram

## Deployment

The API is deployed on Render at: `https://collectposts.onrender.com`

## Project Structure

```
collectPosts/
├── main.py              # FastAPI server
├── scraper.py           # Core scraping logic
├── client_package.py    # Client API
├── requirements.txt     # Dependencies
├── render.yaml         # Render deployment config
└── CLIENT_README.md    # Client documentation
```

## Sources

- ✅ **Reddit**: Working (PRAW API)
- ✅ **YouTube**: Working (API + web scraping)
- ✅ **Instagram**: Working (Instaloader + web scraping)
- ❌ **Quora**: Disabled (anti-bot measures)

That's it! Simple social media scraping with one-line API calls.