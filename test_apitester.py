"""
Test script based on APITester.ipynb
Runs all tests from the notebook
"""

import requests
import pandas as pd
import sys

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
try:
    df1, meta1 = scrape_date_range(
        query="progun",
        sources=["reddit", "youtube"],
        begin_date="2024-11-01",
        end_date="2024-11-15",
        limit=50
    )
    print(f"Result: {len(df1)} posts")
    if len(df1) > 0:
        print(f"Sample columns: {list(df1.columns)[:5]}")
        print(f"Sample source breakdown: {df1['source'].value_counts().to_dict()}")
    print()
except Exception as e:
    print(f"ERROR: {e}")
    print()

print("=" * 70)
print("TEST 2: Testing All Sources (Threads, Quora, Instagram)")
print("=" * 70)
try:
    df2, meta2 = scrape_date_range(
        query="progun",
        sources=["threads"],
        begin_date="2025-11-01",
        end_date="2025-11-17",
        limit=5
    )
    print(f"Threads: {len(df2)} posts")
except Exception as e:
    print(f"Threads ERROR: {e}")

try:
    df3, meta3 = scrape_date_range(
        query="progun",
        sources=["quora"],
        begin_date="2025-11-01",
        end_date="2025-11-17",
        limit=5
    )
    print(f"Quora: {len(df3)} posts")
except Exception as e:
    print(f"Quora ERROR: {e}")

try:
    df4, meta4 = scrape_date_range(
        query="progun",
        sources=["instagram"],
        begin_date="2025-11-01",
        end_date="2025-11-17",
        limit=5
    )
    print(f"Instagram: {len(df4)} posts")
except Exception as e:
    print(f"Instagram ERROR: {e}")
print()

print("=" * 70)
print("TEST 3: Testing Increasing Number of Posts (3-year period)")
print("=" * 70)
try:
    df5, meta5 = scrape_date_range(
        query="progun",
        sources=["reddit", "youtube"],
        begin_date="2022-11-01",
        end_date="2025-11-17",
        limit=5000
    )
    print(f"Result: {len(df5)} posts")
    if len(df5) > 0:
        print(f"Source breakdown: {df5['source'].value_counts().to_dict()}")
        print(f"Sample dates: {df5['timestamp'].head(3).tolist() if 'timestamp' in df5.columns else 'N/A'}")
    print()
except Exception as e:
    print(f"ERROR: {e}")
    print()

print("=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)

