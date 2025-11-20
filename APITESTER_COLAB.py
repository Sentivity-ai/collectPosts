"""
APITester - Colab-Compatible Version
Exact replica of APITester.ipynb tests for external Colab testing
"""

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
    
    # Show limit information if available
    limit_info = result.get('limit_info', {})
    if limit_info:
        print(f"\n📊 Limit Info:")
        print(f"   Requested: {limit_info.get('requested_limit', 'N/A')}")
        print(f"   Effective: {limit_info.get('effective_limit', 'N/A')}")
        if limit_info.get('was_capped', False):
            print(f"   ⚠️  Limit was capped! (reason: {'large_historical' if limit_info.get('is_large_historical') else 'normal'} range, {limit_info.get('num_sources')} sources)")
        else:
            print(f"   ✅ No cap applied")
    
    return df, result

print("=" * 70)
print("TEST 1: Testing Narrow Historical Window")
print("=" * 70)
# Test with a specific narrow historical date range
# You can change these dates to test any narrow window
test_begin_date = "2024-11-01"
test_end_date = "2024-11-15"
print(f"Date range: {test_begin_date} to {test_end_date}")
print("(You can modify these dates in the code to test any narrow historical window)")

df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date=test_begin_date,
    end_date=test_end_date, 
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

