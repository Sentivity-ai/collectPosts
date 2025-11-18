"""
CollectPosts - Colab-Compatible Tester
Test the deployed API service from Google Colab
"""

import requests
import pandas as pd
from IPython.display import display
import time

BASE_URL = "https://collectposts.onrender.com"

def scrape_once(query, sources, limit=100, time_period="week", timeout=300):
    """
    Scrape posts from CollectPosts API
    
    Args:
        query: Search query (e.g., "progun", "Hamilton Beach")
        sources: List of sources (e.g., ["reddit", "youtube"])
        limit: Posts per source (default: 100)
        time_period: "hour", "day", "week", "month", or "year" (default: "week")
        timeout: Request timeout in seconds (default: 200)
    
    Returns:
        df: DataFrame with posts
        meta: Metadata dictionary
    """
    # Map time_period to days
    time_mapping = {
        "hour": 1,
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365
    }
    days = time_mapping.get(time_period.lower(), 7)
    
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        "days": days
    }
    
    try:
        print(f"🔍 Scraping '{query}' from {sources} (last {time_period}, limit={limit})...")
        print(f"📡 Calling API: {BASE_URL}/scrape-multi-source")
        
        response = requests.post(
            f"{BASE_URL}/scrape-multi-source",
            json=payload,
            timeout=timeout
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
            "sources": result.get("sources", sources)
        }
        
        print(f"✅ Success: {len(df)} posts collected")
        if meta["source_breakdown"]:
            print(f"📊 Breakdown: {meta['source_breakdown']}")
        
        return df, meta
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out after {timeout}s. Try reducing limit or time_period."
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}


def test_multiple_periods(query, sources, limit=100, periods=["hour", "day", "week", "month", "year"]):
    """
    Test scraping across multiple time periods
    
    Args:
        query: Search query
        sources: List of sources
        limit: Posts per source
        periods: List of time periods to test
    
    Returns:
        combined_df: Combined DataFrame with all results
        results_dict: Dictionary of results per period
    """
    all_results = []
    results_dict = {}
    
    print(f"🧪 Testing '{query}' across {len(periods)} time periods...")
    print("=" * 60)
    
    for period in periods:
        print(f"\n📅 Testing period: {period}")
        print("-" * 60)
        
        try:
            df, meta = scrape_once(query, sources, limit=limit, time_period=period)
            
            if len(df) > 0:
                df = df.copy()
                df['time_period'] = period
                all_results.append(df)
                results_dict[period] = {"df": df, "meta": meta}
                print(f"✅ {period}: {len(df)} posts")
            else:
                print(f"⚠️  {period}: No posts found")
                results_dict[period] = {"df": pd.DataFrame(), "meta": meta}
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"❌ {period}: Error - {str(e)}")
            results_dict[period] = {"df": pd.DataFrame(), "meta": {"error": str(e)}}
    
    # Combine all results
    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        print("\n" + "=" * 60)
        print(f"📊 Combined Results: {len(combined)} total posts")
        
        if 'time_period' in combined.columns:
            print("\nPost Counts by Period × Source:")
            if 'source' in combined.columns:
                print(combined.groupby(['time_period', 'source']).size().unstack(fill_value=0))
            else:
                print(combined.groupby('time_period').size())
        
        return combined, results_dict
    else:
        print("\n⚠️  No results gathered across the selected periods & sources.")
        print("💡 Try widening periods/sources or increasing LIMIT.")
        return pd.DataFrame(), results_dict


# Example usage for Colab
if __name__ == "__main__":
    # Test parameters - START WITH SMALLER VALUES FOR TESTING
    QUERY = "progun"
    SOURCES = ["reddit", "youtube"]  # Start with fewer sources
    TIME_PERIODS = ["week", "month"]  # Start with fewer periods
    LIMIT = 50  # Start with smaller limit
    TIMEOUT = 300  # Increased timeout
    
    print("🚀 CollectPosts - Full Source × Time Period Tester (Notebook)")
    print("=" * 60)
    print(f"Query: {QUERY}")
    print(f"Sources: {', '.join(SOURCES)}")
    print(f"Time periods: {', '.join(TIME_PERIODS)}")
    print(f"Limit/source: {LIMIT}")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 60)
    
    # Run test
    combined, results = test_multiple_periods(
        query=QUERY,
        sources=SOURCES,
        limit=LIMIT,
        periods=TIME_PERIODS
    )
    
    # Save results
    if len(combined) > 0:
        output_file = f"collectposts_results_{QUERY}_{int(time.time())}.csv"
        combined.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        # Display sample
        print("\n📋 Sample rows:")
        display(combined.head(10))
    else:
        print("\n⚠️  No results gathered across the selected periods & sources.")
        print("💡 Try widening periods/sources or increasing LIMIT.")

