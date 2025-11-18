"""
Exact test from APITester.ipynb
"""

import requests
import pandas as pd
from IPython.display import display

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
print("TEST 1: Testing Back In Time (2024-11-01 to 2024-11-15)")
print("=" * 70)
df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2024-11-01",
    end_date="2024-11-15", 
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
df, meta = scrape_date_range(
    query="progun",
    sources=["threads"],
    begin_date="2025-11-01",
    end_date="2025-11-17", 
    limit=5
)
print(f"Threads: {len(df)} posts")

df1, meta1 = scrape_date_range(
    query="progun",
    sources=["quora"],
    begin_date="2025-11-01",
    end_date="2025-11-17", 
    limit=5
)
print(f"Quora: {len(df1)} posts")

df2, meta2 = scrape_date_range(
    query="progun",
    sources=["instagram"],
    begin_date="2025-11-01",
    end_date="2025-11-17", 
    limit=5
)
print(f"Instagram: {len(df2)} posts")

print("\n" + "=" * 70)
print("TEST 3: Testing Increasing Number of Posts (3-year period)")
print("=" * 70)
df, meta = scrape_date_range(
    query="progun",
    sources=["reddit","youtube"],
    begin_date="2022-11-01",
    end_date="2025-11-17", 
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

