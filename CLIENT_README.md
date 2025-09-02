# CollectPosts Client Package

Simple package to scrape social media posts and get CSV output.

## Installation

```bash
pip install requests pandas
```

## Usage

```python
from client_package import scrape_posts, save_to_csv

# Get posts
df, status = scrape_posts("politics", limit=100)

# Save to CSV
save_to_csv(df, "politics_posts.csv")
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

**Basic scraping:**
```python
df, status = scrape_posts("technology", limit=50)
print(f"Got {len(df)} posts")
```

**Specific sources:**
```python
df, status = scrape_posts("AI", sources=["reddit", "youtube"], limit=100)
```

**Save to file:**
```python
save_to_csv(df, "ai_posts.csv")
```

**Convert to DataFrame for analysis:**
```python
import pandas as pd

# Filter by source
reddit_posts = df[df['source'] == 'reddit']
youtube_posts = df[df['source'] == 'youtube']

# Sort by score
top_posts = df.sort_values('score', ascending=False).head(10)
```

## Environment Variable (Optional)

```bash
export COLLECTPOSTS_URL="https://collectposts.onrender.com"
```

## Output Format

Your CSV will look like:
```csv
title,content,author,score,url,timestamp,source
"Political discussion","Full post content...",username,150,https://...,2025-01-30,reddit
"Tech news video","Video description...",channel,2500,https://...,2025-01-30,youtube
```

That's it! Simple CSV output from social media scraping.
