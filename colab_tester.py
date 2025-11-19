"""
CollectPosts - Colab-Compatible Tester
Test the deployed API service from Google Colab
Supports both time_period and date range testing
"""

import requests
import pandas as pd
from IPython.display import display
import time
from datetime import datetime, timedelta

BASE_URL = "https://collectposts.onrender.com"

def scrape_once(query, sources, limit=100, time_period="week", begin_date=None, end_date=None, timeout=300):
    """
    Scrape posts from CollectPosts API
    
    Args:
        query: Search query (e.g., "progun", "Hamilton Beach")
        sources: List of sources (e.g., ["reddit", "youtube"])
        limit: Posts per source (default: 100)
        time_period: "hour", "day", "week", "month", or "year" (default: "week")
                     Only used if begin_date/end_date are not provided
        begin_date: Start date in "YYYY-MM-DD" format (optional, overrides time_period)
        end_date: End date in "YYYY-MM-DD" format (optional, overrides time_period)
        timeout: Request timeout in seconds (default: 300)
    
    Returns:
        df: DataFrame with posts
        meta: Metadata dictionary
    """
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit
    }
    
    # Use date range if provided, otherwise use time_period
    if begin_date and end_date:
        payload["begin_date"] = begin_date
        payload["end_date"] = end_date
        print(f"📅 Using date range: {begin_date} to {end_date}")
    else:
        # Map time_period to days
        time_mapping = {
            "hour": 1,
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365
        }
        days = time_mapping.get(time_period.lower(), 7)
        payload["days"] = days
        print(f"📅 Using time period: {time_period} ({days} days)")
    
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


def test_date_ranges(query, sources, limit=100, date_ranges=None, timeout=300):
    """
    Test scraping with specific date ranges (for historical data testing)
    
    Args:
        query: Search query
        sources: List of sources
        limit: Posts per source
        date_ranges: List of (begin_date, end_date) tuples in "YYYY-MM-DD" format
        timeout: Request timeout
    
    Returns:
        results_dict: Dictionary of results per date range
    """
    if date_ranges is None:
        # Default test cases
        now = datetime.utcnow()
        two_weeks_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d")
        one_month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        three_months_ago = (now - timedelta(days=90)).strftime("%Y-%m-%d")
        one_year_ago = (now - timedelta(days=365)).strftime("%Y-%m-%d")
        three_years_ago = (now - timedelta(days=365*3)).strftime("%Y-%m-%d")
        now_str = now.strftime("%Y-%m-%d")
        
        date_ranges = [
            ("2024-11-01", "2024-11-15"),  # Narrow historical window
            (two_weeks_ago, now_str),  # Two weeks ago
            (one_month_ago, now_str),  # One month ago
            (three_years_ago, now_str),  # 3-year period
        ]
    
    results_dict = {}
    
    print(f"🧪 Testing '{query}' with {len(date_ranges)} date ranges...")
    print("=" * 70)
    
    for begin_date, end_date in date_ranges:
        print(f"\n📅 Testing: {begin_date} to {end_date}")
        print("-" * 70)
        
        try:
            df, meta = scrape_once(
                query=query,
                sources=sources,
                limit=limit,
                begin_date=begin_date,
                end_date=end_date,
                timeout=timeout
            )
            
            results_dict[f"{begin_date}_{end_date}"] = {
                "df": df,
                "meta": meta,
                "begin_date": begin_date,
                "end_date": end_date
            }
            
            if len(df) > 0:
                print(f"✅ {len(df)} posts found")
                if meta.get("source_breakdown"):
                    print(f"📊 Breakdown: {meta['source_breakdown']}")
            else:
                print(f"⚠️  No posts found")
            
            time.sleep(1)  # Small delay to avoid rate limiting
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results_dict[f"{begin_date}_{end_date}"] = {
                "df": pd.DataFrame(),
                "meta": {"error": str(e)},
                "begin_date": begin_date,
                "end_date": end_date
            }
    
    return results_dict


# Example usage for Colab
if __name__ == "__main__":
    # Test parameters - START WITH SMALLER VALUES FOR TESTING
    QUERY = "progun"
    SOURCES = ["reddit", "youtube"]  # Start with fewer sources
    LIMIT = 50  # Start with smaller limit
    TIMEOUT = 300  # Increased timeout
    
    print("🚀 CollectPosts - External API Tester (Colab)")
    print("=" * 70)
    print(f"Query: {QUERY}")
    print(f"Sources: {', '.join(SOURCES)}")
    print(f"Limit/source: {LIMIT}")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 70)
    
    # TEST 1: Narrow historical window (2 weeks ago)
    print("\n" + "=" * 70)
    print("TEST 1: Two Weeks Ago")
    print("=" * 70)
    now = datetime.utcnow()
    two_weeks_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d")
    now_str = now.strftime("%Y-%m-%d")
    df1, meta1 = scrape_once(QUERY, SOURCES, limit=LIMIT, begin_date=two_weeks_ago, end_date=now_str, timeout=TIMEOUT)
    print(f"Result: {len(df1)} posts\n")
    
    # TEST 2: Narrow historical window (specific dates)
    print("=" * 70)
    print("TEST 2: Specific Date Range (2024-11-01 to 2024-11-15)")
    print("=" * 70)
    df2, meta2 = scrape_once(QUERY, SOURCES, limit=LIMIT, begin_date="2024-11-01", end_date="2024-11-15", timeout=TIMEOUT)
    print(f"Result: {len(df2)} posts\n")
    
    # TEST 3: 3-year period
    print("=" * 70)
    print("TEST 3: 3-Year Period")
    print("=" * 70)
    three_years_ago = (now - timedelta(days=365*3)).strftime("%Y-%m-%d")
    df3, meta3 = scrape_once(QUERY, SOURCES, limit=500, begin_date=three_years_ago, end_date=now_str, timeout=TIMEOUT)
    print(f"Result: {len(df3)} posts\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"TEST 1 (2 weeks ago): {len(df1)} posts")
    print(f"TEST 2 (2024-11-01 to 2024-11-15): {len(df2)} posts")
    print(f"TEST 3 (3-year period): {len(df3)} posts")
    
    # Save results
    if len(df1) > 0 or len(df2) > 0 or len(df3) > 0:
        output_file = f"collectposts_test_{QUERY}_{int(time.time())}.csv"
        all_dfs = []
        if len(df1) > 0:
            df1_copy = df1.copy()
            df1_copy['test'] = '2_weeks_ago'
            all_dfs.append(df1_copy)
        if len(df2) > 0:
            df2_copy = df2.copy()
            df2_copy['test'] = 'narrow_historical'
            all_dfs.append(df2_copy)
        if len(df3) > 0:
            df3_copy = df3.copy()
            df3_copy['test'] = '3_year_period'
            all_dfs.append(df3_copy)
        
        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            combined.to_csv(output_file, index=False)
            print(f"\n💾 Results saved to: {output_file}")
            
            # Display sample
            print("\n📋 Sample rows:")
            display(combined.head(10))
    else:
        print("\n⚠️  No results gathered. Check API status and parameters.")

