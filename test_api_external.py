#!/usr/bin/env python3
"""
External API Test Script
Tests the deployed API service without using local env files
"""

import requests
import pandas as pd
import json
from datetime import datetime

BASE = "https://collectposts.onrender.com"

def scrape(query, sources, limit=500, **kwargs):
    """Scrape posts from the API"""
    payload = {
        "query": query,
        "sources": sources,
        "limit_per_source": limit,
        **kwargs
    }
    
    print(f"Calling API: {BASE}/scrape-multi-source")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        r = requests.post(f"{BASE}/scrape-multi-source", json=payload, timeout=200)
        r.raise_for_status()
        meta = r.json()
        posts = meta.get("all_posts", meta.get("data", []))
        if not isinstance(posts, list):
            posts = [posts]
        df = pd.DataFrame(posts)
        return df, meta
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise

def test_api_health():
    """Test if API is alive"""
    try:
        r = requests.get(f"{BASE}/health", timeout=10)
        r.raise_for_status()
        print("API Health Check: PASS")
        print(f"Response: {r.json()}")
        return True
    except Exception as e:
        print(f"API Health Check: FAIL - {e}")
        return False

def test_api_root():
    """Test API root endpoint"""
    try:
        r = requests.get(f"{BASE}/", timeout=10)
        r.raise_for_status()
        print("API Root Check: PASS")
        print(f"Response: {r.json()}")
        return True
    except Exception as e:
        print(f"API Root Check: FAIL - {e}")
        return False

def main():
    """Run API tests"""
    print("=" * 60)
    print("External API Test - CollectPosts")
    print("=" * 60)
    print(f"Base URL: {BASE}\n")
    
    # Test 1: Health check
    print("TEST 1: Health Check")
    print("-" * 60)
    if not test_api_health():
        print("\nAPI is not responding. Check deployment status.")
        return
    print()
    
    # Test 2: Root endpoint
    print("TEST 2: Root Endpoint")
    print("-" * 60)
    test_api_root()
    print()
    
    # Test 3: Actual scraping
    print("TEST 3: Scraping Test")
    print("-" * 60)
    try:
        df, meta = scrape(
            "Hamilton Beach",
            ["reddit", "youtube"],
            limit=100,
            days=30
        )
        
        print(f"\nResults:")
        print(f"  Total posts: {len(df)}")
        print(f"  Sources: {meta.get('source_breakdown', {})}")
        print(f"  Hashtags: {len(meta.get('hashtags', []))}")
        
        if len(df) > 0:
            print(f"\nSample posts:")
            print(df.head(3).to_string())
            print("\nPASS: Scraping test successful")
        else:
            print("\nWARNING: No posts collected")
            
    except Exception as e:
        print(f"\nFAIL: Scraping test failed - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

