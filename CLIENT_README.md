# CollectPosts Client Package

Simple package to scrape social media posts and get data directly.

## Installation

```bash
pip install requests pandas
```

## Usage

```python
from client_package import api

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

**General topic search:**
```python
data, status = api(query="technology", limit=50)
```

**Specific sources:**
```python
data, status = api(query="AI", sources=["reddit", "youtube"], limit=100)
```

**Time periods:**
```python
data, status = api(subreddit="politics", time_passed="month", limit=200)
```

**Work with the data:**
```python
# Filter by source
reddit_posts = data[data['source'] == 'reddit']
youtube_posts = data[data['source'] == 'youtube']

# Sort by score
top_posts = data.sort_values('score', ascending=False).head(10)

# Save to CSV if needed
data.to_csv("my_posts.csv", index=False)
```

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

That's it! Data drops directly into your script as a DataFrame.
