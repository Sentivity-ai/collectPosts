import requests
import pandas as pd
import os

def scrape_posts(query, sources=None, limit=100, days=30, base_url=None):
    """Scrape social media posts and return DataFrame"""
    if sources is None:
        sources = ['reddit', 'youtube', 'instagram']
    
    base_url = base_url or os.getenv('COLLECTPOSTS_URL', 'https://collectposts.onrender.com')
    
    payload = {
        "query": query,
        "sources": sources,
        "limit": limit,
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

def save_to_csv(df, filename):
    """Save DataFrame to CSV"""
    df.to_csv(filename, index=False)
    return f"Saved {len(df)} posts to {filename}"

# Example usage
if __name__ == "__main__":
    # Scrape posts
    df, status = scrape_posts("politics", limit=50)
    
    if not df.empty:
        print(f"Status: {status}")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:")
        print(df.head())
        
        # Save to CSV
        result = save_to_csv(df, "politics_posts.csv")
        print(result)
    else:
        print(f"Error: {status}")
