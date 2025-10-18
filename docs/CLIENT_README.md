# CollectPosts Client Package

Simple package to scrape social media posts from **5 platforms** and get data directly.

## 🚀 Supported Platforms

- **Reddit**: Subreddit posts, comments, engagement metrics
- **YouTube**: Video titles, descriptions, view counts  
- **Instagram**: Posts, captions, likes, timestamps
- **Quora**: Questions, answers, upvotes
- **Threads**: Posts, engagement, timestamps

## Installation

```bash
pip install requests pandas
```

## Usage

```python
from client import api

# Get posts directly into your script
data, status = api(subreddit="labubu", limit="100", time_passed="week")

# Data is now in the 'data' variable as a DataFrame
print(f"Got {len(data)} posts")
print(data.head())
```

## What You Get

**CSV with columns:**
- title: Post title/content
- content: Full post text
- author: Username/creator
- score: Engagement metrics
- url: Link to post
- timestamp: When posted
- source: reddit/youtube/instagram

## Examples

**Your exact example:**
```python
data, status = api(subreddit="labubu", limit="100", time_passed="week")
```

**All platforms search:**
```python
data, status = api(query="AI technology", sources=["reddit", "youtube", "instagram", "quora", "threads"], limit=50)
```

**Specific sources:**
```python
data, status = api(query="politics", sources=["reddit", "quora"], limit=100)
```

**Time periods:**
```python
data, status = api(subreddit="politics", time_passed="month", limit=200)
```

**Recent posts only:**
```python
data, status = api(query="technology", time_passed="day", limit=50)
```

**Work with the data:**
```python
# Filter by source
reddit_posts = data[data['source'] == 'reddit']
youtube_posts = data[data['source'] == 'youtube']
quora_posts = data[data['source'] == 'quora']
threads_posts = data[data['source'] == 'threads']
instagram_posts = data[data['source'] == 'instagram']

# Sort by score
top_posts = data.sort_values('score', ascending=False).head(10)

# Analyze by platform
platform_counts = data['source'].value_counts()
print(f"Posts by platform: {platform_counts}")

# Save to CSV if needed
data.to_csv("my_posts.csv", index=False)
```

## 🏷️ Hashtag Generation

The API now automatically generates hashtags from all collected posts:

```python
# Hashtags are included in the API response
response = requests.post("https://collectposts.onrender.com/scrape-multi-source", json={
    "query": "AI technology",
    "sources": ["reddit", "youtube", "instagram", "quora", "threads"],
    "limit": 50,
    "days": 7
})

result = response.json()
hashtags = result.get('hashtags', [])
print(f"Generated hashtags: {hashtags}")
```

## ⏰ Time Filtering

All platforms now support precise time filtering:

- **hour**: Last hour
- **day**: Last 24 hours  
- **week**: Last 7 days
- **month**: Last 30 days
- **year**: Last 365 days

## Environment Variable (Optional)

```bash
export COLLECTPOSTS_URL="https://collectposts.onrender.com"
```

## Output Format

Your DataFrame will have these columns:
```python
# data.columns
['title', 'content', 'author', 'score', 'url', 'timestamp', 'source']

# Sample data
print(data.head())
```

Finito! Data drops directly into your script as a DataFrame.
