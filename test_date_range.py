"""
CollectPosts - Date Range Testing Code
Test the API with specific begin_date and end_date parameters
"""

import requests
import pandas as pd
from IPython.display import display
from datetime import datetime, timedelta

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
        print(f"📡 Calling API: {BASE_URL}/scrape-multi-source")
        
        response = requests.post(
            f"{BASE_URL}/scrape-multi-source",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Extract posts
        posts = result.get("all_posts", result.get("data", []))
        if not isinstance(posts, list):
            posts = [posts] if posts else []
        
        df = pd.DataFrame(posts)
        meta = {
            "total_posts": result.get("total_posts", len(df)),
            "source_breakdown": result.get("source_breakdown", {}),
            "hashtags": result.get("hashtags", []),
            "query": result.get("query", query),
            "sources": result.get("sources", sources),
            "date_range": f"{begin_date} to {end_date}"
        }
        
        print(f"✅ Success: {len(df)} posts collected")
        if meta["source_breakdown"]:
            print(f"📊 Breakdown: {meta['source_breakdown']}")
        
        return df, meta
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out. Try reducing limit or date range."
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text[:200]}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}


# ============================================================================
# EXAMPLE 1: Specific Date Range (Last Month)
# ============================================================================
print("=" * 70)
print("EXAMPLE 1: Last Month (November 2024)")
print("=" * 70)

df1, meta1 = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2024-10-15",
    end_date="2024-11-15",
    limit=30
)

if len(df1) > 0:
    print(f"\n📋 Sample Results ({len(df1)} total posts):")
    display(df1.head(10))
    print(f"\n💾 Full results available in DataFrame 'df1'")
else:
    print("\n⚠️  No posts found in this date range")


# ============================================================================
# EXAMPLE 2: Specific Date Range (Last Quarter)
# ============================================================================
print("\n" + "=" * 70)
print("EXAMPLE 2: Last Quarter (Q4 2024)")
print("=" * 70)

df2, meta2 = scrape_date_range(
    query="progun",
    sources=["reddit"],
    begin_date="2024-10-01",
    end_date="2024-12-31",
    limit=50
)

if len(df2) > 0:
    print(f"\n📋 Sample Results ({len(df2)} total posts):")
    display(df2.head(10))
    print(f"\n💾 Full results available in DataFrame 'df2'")
else:
    print("\n⚠️  No posts found in this date range")


# ============================================================================
# EXAMPLE 3: Custom Date Range (Any dates)
# ============================================================================
print("\n" + "=" * 70)
print("EXAMPLE 3: Custom Date Range")
print("=" * 70)
print("To use your own dates, modify the parameters below:\n")

# Customize these values:
CUSTOM_QUERY = "progun"
CUSTOM_SOURCES = ["reddit", "youtube"]
CUSTOM_BEGIN_DATE = "2024-01-01"  # Change this
CUSTOM_END_DATE = "2024-03-31"    # Change this
CUSTOM_LIMIT = 30

df3, meta3 = scrape_date_range(
    query=CUSTOM_QUERY,
    sources=CUSTOM_SOURCES,
    begin_date=CUSTOM_BEGIN_DATE,
    end_date=CUSTOM_END_DATE,
    limit=CUSTOM_LIMIT
)

if len(df3) > 0:
    print(f"\n📋 Sample Results ({len(df3)} total posts):")
    display(df3.head(10))
    
    # Save to CSV
    output_file = f"collectposts_{CUSTOM_QUERY}_{CUSTOM_BEGIN_DATE}_to_{CUSTOM_END_DATE}.csv"
    df3.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
else:
    print("\n⚠️  No posts found in this date range")


# ============================================================================
# QUICK REFERENCE
# ============================================================================
print("\n" + "=" * 70)
print("QUICK REFERENCE")
print("=" * 70)
print("""
Function: scrape_date_range(query, sources, begin_date, end_date, limit)

Parameters:
  - query: Search term (string)
  - sources: List of sources (e.g., ["reddit", "youtube"])
  - begin_date: Start date in "YYYY-MM-DD" format
  - end_date: End date in "YYYY-MM-DD" format
  - limit: Maximum posts per source (default: 50)

Returns:
  - df: pandas DataFrame with all posts
  - meta: Dictionary with metadata (total_posts, source_breakdown, etc.)

Example:
  df, meta = scrape_date_range(
      query="Hamilton Beach",
      sources=["reddit", "youtube"],
      begin_date="2024-01-01",
      end_date="2024-12-31",
      limit=100
  )
""")

