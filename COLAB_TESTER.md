# CollectPosts - Colab Tester

## Quick Start

Copy this code into a Google Colab cell:

```python
import requests
import pandas as pd
from IPython.display import display
import time

BASE_URL = "https://collectposts.onrender.com"

def scrape_once(query, sources, limit=100, time_period="week", timeout=200):
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
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text[:200]}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {error_msg}")
        return pd.DataFrame(), {"error": error_msg}


# Example usage
df, meta = scrape_once("progun", ["reddit", "youtube"], limit=50, time_period="week")
print(f"\n📊 Total posts: {len(df)}")
if len(df) > 0:
    display(df.head(10))
```

## Full Multi-Period Tester

For testing across multiple time periods:

```python
def test_multiple_periods(query, sources, limit=100, periods=["hour", "day", "week", "month", "year"]):
    """Test scraping across multiple time periods"""
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
            
            time.sleep(1)  # Small delay to avoid rate limiting
            
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


# Run full test
QUERY = "progun"
SOURCES = ["reddit", "youtube", "instagram", "quora", "threads"]
TIME_PERIODS = ["hour", "day", "week", "month", "year"]
LIMIT = 100

combined, results = test_multiple_periods(QUERY, SOURCES, limit=LIMIT, periods=TIME_PERIODS)

if len(combined) > 0:
    output_file = f"collectposts_results_{QUERY}_{int(time.time())}.csv"
    combined.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
    display(combined.head(10))
```

