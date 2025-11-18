# CollectPosts - Date Range Testing Guide

## Quick Start: Test with Specific Date Range

Copy this code into Google Colab:

```python
import requests
import pandas as pd
from IPython.display import display

BASE_URL = "https://collectposts.onrender.com"

def scrape_date_range(query, sources, begin_date, end_date, limit=50):
    """
    Scrape posts from CollectPosts API for a specific date range
    
    Args:
        query: Search query (e.g., "progun", "Hamilton Beach")
        sources: List of sources (e.g., ["reddit", "youtube"])
        begin_date: Start date in "YYYY-MM-DD" format (e.g., "2024-01-01")
        end_date: End date in "YYYY-MM-DD" format (e.g., "2024-12-31")
        limit: Posts per source (default: 50)
    
    Returns:
        df: DataFrame with posts
        meta: Metadata dictionary
    """
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        "begin_date": begin_date,
        "end_date": end_date
    }
    
    try:
        print(f"🔍 Scraping '{query}' from {sources}")
        print(f"📅 Date Range: {begin_date} to {end_date}")
        
        response = requests.post(
            f"{BASE_URL}/scrape-multi-source",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        
        result = response.json()
        posts = result.get("all_posts", result.get("data", []))
        if not isinstance(posts, list):
            posts = [posts] if posts else []
        
        df = pd.DataFrame(posts)
        meta = {
            "total_posts": result.get("total_posts", len(df)),
            "source_breakdown": result.get("source_breakdown", {}),
            "hashtags": result.get("hashtags", [])
        }
        
        print(f"✅ Success: {len(df)} posts collected")
        print(f"📊 Breakdown: {meta['source_breakdown']}")
        
        return df, meta
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return pd.DataFrame(), {"error": str(e)}


# Example: Last Month
df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2024-10-15",
    end_date="2024-11-15",
    limit=30
)

if len(df) > 0:
    display(df.head(10))
    # Save to CSV
    df.to_csv("results.csv", index=False)
    print("💾 Saved to results.csv")
```

## Examples

### Example 1: Last Month
```python
df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2024-10-15",
    end_date="2024-11-15",
    limit=30
)
```

### Example 2: Last Quarter
```python
df, meta = scrape_date_range(
    query="Hamilton Beach",
    sources=["reddit", "youtube"],
    begin_date="2024-10-01",
    end_date="2024-12-31",
    limit=50
)
```

### Example 3: Specific Year
```python
df, meta = scrape_date_range(
    query="technology",
    sources=["reddit"],
    begin_date="2024-01-01",
    end_date="2024-12-31",
    limit=100
)
```

## Parameters

- **query**: Your search term (string)
- **sources**: List of platforms (e.g., `["reddit", "youtube"]`)
- **begin_date**: Start date in `"YYYY-MM-DD"` format
- **end_date**: End date in `"YYYY-MM-DD"` format
- **limit**: Maximum posts per source (recommended: 20-50)

## Date Format

Dates must be in **YYYY-MM-DD** format:
- ✅ Correct: `"2024-01-15"`
- ❌ Wrong: `"01/15/2024"` or `"January 15, 2024"`

## Tips

1. **Start small**: Use limit=20-30 for testing
2. **One source first**: Test with `["reddit"]` before adding more
3. **Shorter ranges**: Narrow date ranges are faster
4. **Save results**: Use `df.to_csv("filename.csv")` to save

