"""
CollectPosts - Date Range Testing Code
Ready-to-use code for testing specific date ranges
"""

import requests
import pandas as pd
from IPython.display import display

BASE_URL = "https://collectposts.onrender.com"

def scrape_date_range(query, sources, begin_date, end_date, limit=50):
    """
    Scrape posts from CollectPosts API for a specific date range
    
    Parameters:
        query: Search query (e.g., "progun", "Hamilton Beach")
        sources: List of sources (e.g., ["reddit", "youtube"])
        begin_date: Start date in "YYYY-MM-DD" format
        end_date: End date in "YYYY-MM-DD" format
        limit: Posts per source (default: 50)
    
    Returns:
        df: DataFrame with posts
        meta: Metadata dictionary with total_posts, source_breakdown, etc.
    """
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        "begin_date": begin_date,
        "end_date": end_date
    }
    
    try:
        print(f"Scraping '{query}' from {sources}")
        print(f"Date Range: {begin_date} to {end_date}")
        
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
            "hashtags": result.get("hashtags", []),
            "date_range": f"{begin_date} to {end_date}"
        }
        
        print(f"Success: {len(df)} posts collected")
        print(f"Breakdown: {meta['source_breakdown']}")
        
        return df, meta
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return pd.DataFrame(), {"error": str(e)}


# ============================================================================
# EXAMPLE USAGE - Modify these values for your test
# ============================================================================

# Example 1: Last 2 weeks
df, meta = scrape_date_range(
    query="progun",
    sources=["reddit", "youtube"],
    begin_date="2025-11-01",
    end_date="2025-11-15",
    limit=30
)

# Display results
if len(df) > 0:
    print(f"\nTotal posts: {len(df)}")
    display(df.head(10))
    
    # Save to CSV
    df.to_csv("collectposts_results.csv", index=False)
    print("\nResults saved to: collectposts_results.csv")
else:
    print("\nNo posts found in this date range")

