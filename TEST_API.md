# API Testing Guide

## Quick Test Code

```python
import requests, pandas as pd
BASE = "https://collectposts.onrender.com"

def scrape(query, sources, limit=500, **kwargs):
    payload = {"query": query, "sources": sources, "limit_per_source": limit, **kwargs}
    r = requests.post(f"{BASE}/scrape-multi-source", json=payload, timeout=200)
    r.raise_for_status()
    meta = r.json()
    posts = meta.get("all_posts", meta.get("data", []))
    if not isinstance(posts, list):
        posts = [posts]
    df = pd.DataFrame(posts)
    return df, meta

# Example usage
df, meta = scrape("Hamilton Beach", ["reddit", "youtube"], limit=1000, days=365)
print(len(df), "posts found")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
df
```

## Parameters

### Required:
- **`query`** (string): Search term, e.g., "Hamilton Beach", "technology", "coffee"
- **`sources`** (list): List of sources to scrape, e.g., `["reddit", "youtube"]`

### Optional:
- **`limit`** (int, default=500): Maximum posts per source
- **`days`** (int, default=7): Number of days to look back
  - Common values: `1`, `7`, `30`, `365`
- **`begin_date`** (string, optional): Start date in `YYYY-MM-DD` format
- **`end_date`** (string, optional): End date in `YYYY-MM-DD` format

### Available Sources:
- `"reddit"` - Reddit posts and comments
- `"youtube"` - YouTube videos
- `"instagram"` - Instagram posts
- `"quora"` - Quora questions and answers
- `"threads"` - Threads posts

## Examples

### Example 1: Basic search
```python
df, meta = scrape("coffee", ["reddit", "youtube"], limit=100, days=30)
```

### Example 2: Specific date range
```python
df, meta = scrape(
    "Hamilton Beach",
    ["reddit", "youtube"],
    limit=500,
    begin_date="2024-01-01",
    end_date="2024-12-31"
)
```

### Example 3: All sources, 1 year
```python
df, meta = scrape(
    "technology",
    ["reddit", "youtube", "instagram", "quora", "threads"],
    limit=1000,
    days=365
)
```

### Example 4: Quick test (small limit)
```python
df, meta = scrape("test", ["reddit"], limit=10, days=7)
print(f"Found {len(df)} posts")
print(df.head())
```

## Response Format

The function returns:
- **`df`**: pandas DataFrame with columns:
  - `title`, `content`, `author`, `url`, `source`, `score`, `created_utc`, etc.
- **`meta`**: Dictionary with:
  - `total_posts`: Total number of posts
  - `source_breakdown`: Posts per source
  - `hashtags`: List of extracted hashtags
  - `query`, `sources`, `days`: Your input parameters

## Notes

- YouTube has a hard limit of 50 posts (to prevent API issues)
- Reddit generates hashtags that are used to query other sources
- The API uses hardcoded credentials, no env files needed
- Timeout is set to 200 seconds for large queries

