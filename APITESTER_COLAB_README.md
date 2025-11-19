# APITester - Colab Version

This is the exact replica of APITester.ipynb for external Colab testing.

## Quick Start

1. Open a new Colab notebook
2. Copy and paste the entire code below into a code cell
3. Run it

## Code (Copy-Paste Ready)

```python
import requests
import pandas as pd
from IPython.display import display
from datetime import datetime, timedelta

BASE_URL = "https://collectposts.onrender.com"

def scrape_date_range(query, sources, begin_date, end_date, limit=500):
    """Scrape posts for a specific date range"""
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        "begin_date": begin_date,
        "end_date": end_date
    }
    response = requests.post(
        f"{BASE_URL}/scrape-multi-source",
        json=payload,
        timeout=300
    )
    response.raise_for_status()
    result = response.json()
    posts = result.get("all_posts", [])
    df = pd.DataFrame(posts)
    print(f"Success: {len(df)} posts collected")
    print(f"Breakdown: {result.get('source_breakdown', {})}")
    return df, result

print("=" * 70)
print("TEST 1: Testing Narrow Historical Window (2 weeks ago)")
print("=" * 70)
# Use dynamic date range - 2 weeks ago to now
now = datetime.utcnow()
two_weeks_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d")
now_str = now.strftime("%Y-%m-%d")
print(f"Date range: {two_weeks_ago} to {now_str}")

df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date=two_weeks_ago,
    end_date=now_str, 
    limit=50
)
print(f"\nDataFrame shape: {df.shape}")
if len(df) > 0:
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nSource breakdown:")
    print(df['source'].value_counts() if 'source' in df.columns else "N/A")
else:
    print("\nNo posts found")

print("\n" + "=" * 70)
print("TEST 2: Testing All Sources (Threads, Quora, Instagram)")
print("=" * 70)
# Use dynamic date range - recent period (last month)
one_month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
print(f"Date range: {one_month_ago} to {now_str}")

df, meta = scrape_date_range(
    query="progun",
    sources=["threads"],
    begin_date=one_month_ago,
    end_date=now_str, 
    limit=5
)
print(f"Threads: {len(df)} posts")

df1, meta1 = scrape_date_range(
    query="progun",
    sources=["quora"],
    begin_date=one_month_ago,
    end_date=now_str, 
    limit=5
)
print(f"Quora: {len(df1)} posts")

df2, meta2 = scrape_date_range(
    query="progun",
    sources=["instagram"],
    begin_date=one_month_ago,
    end_date=now_str, 
    limit=5
)
print(f"Instagram: {len(df2)} posts")

print("\n" + "=" * 70)
print("TEST 3: Testing Increasing Number of Posts (3-year period)")
print("=" * 70)
# Use dynamic date range - 3 years ago to now
three_years_ago = (now - timedelta(days=365*3)).strftime("%Y-%m-%d")
print(f"Date range: {three_years_ago} to {now_str}")

df, meta = scrape_date_range(
    query="progun",
    sources=["reddit","youtube"],
    begin_date=three_years_ago,
    end_date=now_str, 
    limit=5000
)
print(f"\nDataFrame shape: {df.shape}")
if len(df) > 0:
    print(f"\nSource breakdown:")
    print(df['source'].value_counts() if 'source' in df.columns else "N/A")
    print(f"\nSample dates:")
    if 'timestamp' in df.columns:
        print(df['timestamp'].head(5).tolist())

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
```

## What Gets Tested

- **TEST 1**: Narrow historical window (2 weeks ago to now) - tests recent historical data
- **TEST 2**: All sources (Threads, Quora, Instagram) - last month period
- **TEST 3**: 3-year period (3 years ago to now) with high limit - tests large historical ranges

## Expected Results

- **TEST 1**: Should return posts (32+ posts expected)
- **TEST 2**: May return 0 posts (expected for Threads/Quora/Instagram without full auth)
- **TEST 3**: Should return 300+ posts (Reddit + YouTube)

