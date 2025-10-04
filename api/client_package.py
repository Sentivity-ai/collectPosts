import requests
import pandas as pd
import os

def api(subreddit=None, query=None, limit=100, time_passed="week", sources=None, base_url=None):
    """API function that returns data directly - works like api(subreddit="labubu", limit="100", time_passed="week")"""
    
    # Convert time_passed to days
    time_mapping = {
        "hour": 1,
        "day": 1, 
        "week": 7,
        "month": 30,
        "year": 365
    }
    days = time_mapping.get(time_passed, 7)
    
    # Use subreddit as query if provided, otherwise use query
    search_query = subreddit if subreddit else query
    if not search_query:
        return pd.DataFrame(), "Error: Must provide either subreddit or query"
    
    # Default sources if not specified
    if sources is None:
        sources = ['reddit', 'youtube', 'instagram']
    
    base_url = base_url or os.getenv('COLLECTPOSTS_URL', 'https://collectposts.onrender.com')
    
    payload = {
        "query": search_query,
        "sources": sources,
        "limit": int(limit),
        "days": days
    }
    
    try:
        response = requests.post(f"{base_url}/scrape-multi-source", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            return pd.DataFrame(), f"Error: {result['error']}"
        
        posts = result.get('all_posts', [])
        df = pd.DataFrame(posts)
        
        return df, f"Success: {len(df)} posts collected"
        
    except Exception as e:
        return pd.DataFrame(), f"Failed: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Your exact example
    data, status = api(subreddit="labubu", limit="100", time_passed="week")
    
    if not data.empty:
        print(f"Status: {status}")
        print(f"Data shape: {data.shape}")
        print(f"Columns: {list(data.columns)}")
        print(f"Sample data:")
        print(data.head())
        
        # Data is now in the 'data' variable as a DataFrame
        # You can do whatever you want with it
        print(f"\nTotal posts: {len(data)}")
        print(f"Sources: {data['source'].value_counts()}")
    else:
        print(f"Error: {status}")
