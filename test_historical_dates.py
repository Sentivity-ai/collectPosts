"""
Test script for historical date ranges
Uses APITester.ipynb format
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

# Test 1: Historical dates (2024-11-01 to 2024-11-15)
print("=" * 70)
print("TEST 1: Historical Dates (2024-11-01 to 2024-11-15)")
print("=" * 70)
df1, meta1 = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2024-11-01",
    end_date="2024-11-15",
    limit=50
)
print(f"\nResult: {len(df1)} posts")
if len(df1) > 0:
    display(df1.head(5))

# Test 2: 3-year period
print("\n" + "=" * 70)
print("TEST 2: 3-Year Period (2022-01-01 to 2025-01-01)")
print("=" * 70)
df2, meta2 = scrape_date_range(
    query="progun",
    sources=["reddit"],
    begin_date="2022-01-01",
    end_date="2025-01-01",
    limit=70
)
print(f"\nResult: {len(df2)} posts")
if len(df2) > 0:
    display(df2.head(5))

# Test 3: Recent dates (should work)
print("\n" + "=" * 70)
print("TEST 3: Recent Dates (Last 2 weeks)")
print("=" * 70)
from datetime import datetime, timedelta
end = datetime.now()
begin = end - timedelta(days=14)
df3, meta3 = scrape_date_range(
    query="progun",
    sources=["reddit"],
    begin_date=begin.strftime("%Y-%m-%d"),
    end_date=end.strftime("%Y-%m-%d"),
    limit=20
)
print(f"\nResult: {len(df3)} posts")
if len(df3) > 0:
    display(df3.head(5))

