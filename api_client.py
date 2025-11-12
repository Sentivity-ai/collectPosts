#!/usr/bin/env python3
"""
CollectPosts API Client
External client for calling the deployed API service
No local env files needed - uses hardcoded credentials in the API
"""

import requests
import pandas as pd

BASE = "https://collectposts.onrender.com"

def scrape(query, sources, limit=500, **kwargs):
    """
    Scrape posts from the CollectPosts API
    
    Args:
        query: Search query (e.g., "Hamilton Beach")
        sources: List of sources (e.g., ["reddit", "youtube"])
        limit: Posts per source (default: 500)
        **kwargs: Additional parameters (days, begin_date, end_date)
    
    Returns:
        df: DataFrame with posts
        meta: Metadata dictionary
    """
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        **kwargs
    }
    
    r = requests.post(f"{BASE}/scrape-multi-source", json=payload, timeout=200)
    r.raise_for_status()
    meta = r.json()
    posts = meta.get("all_posts", meta.get("data", []))
    if not isinstance(posts, list):
        posts = [posts]
    df = pd.DataFrame(posts)
    return df, meta

if __name__ == "__main__":
    # Example usage
    df, meta = scrape("Hamilton Beach", ["reddit", "youtube"], limit=1000, days=365)
    print(len(df), "posts found")
    
    # Set pandas display options to show the full DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print("\nDataFrame:")
    print(df)
    
    print("\nMetadata:")
    print(f"Sources: {meta.get('source_breakdown', {})}")
    print(f"Hashtags: {len(meta.get('hashtags', []))}")

