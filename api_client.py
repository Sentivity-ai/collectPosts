#!/usr/bin/env python3
"""
Simple API Client for CollectPosts Service
Transform your web service into simple one-line API calls
"""

import requests
import json
import os
from typing import List, Dict, Optional, Union
from datetime import datetime

class CollectPostsAPI:
    """Simple API client for CollectPosts service"""
    
    def __init__(self, base_url: str = None):
        """
        Initialize API client
        
        Args:
            base_url: Your Render service URL (e.g., 'https://your-app.onrender.com')
                      If None, will try to get from COLLECTPOSTS_URL env var
        """
        self.base_url = base_url or os.getenv('COLLECTPOSTS_URL', 'http://localhost:8000')
        if not self.base_url.startswith('http'):
            self.base_url = f'https://{self.base_url}'
    
    def scrape(self, query: str, sources: List[str] = None, limit: int = 100, days: int = 30) -> Dict:
        """
        One-line call to scrape social media posts
        
        Args:
            query: Search term (e.g., 'politics', 'tech', 'sports')
            sources: List of sources ['reddit', 'youtube', 'instagram'] (default: all)
            limit: Maximum posts per source (default: 100)
            days: Lookback period in days (default: 30)
        
        Returns:
            Dict with scraped data and hashtags
        
        Example:
            api.scrape('politics', limit=200)  # One line!
        """
        if sources is None:
            sources = ['reddit', 'youtube', 'instagram']
        
        payload = {
            "query": query,
            "sources": sources,
            "limit": limit,
            "days": days
        }
        
        try:
            response = requests.post(f"{self.base_url}/scrape-multi-source", 
                                  json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def get_hashtags(self, posts: List[Dict], max_hashtags: int = 50) -> List[str]:
        """
        Generate hashtags from posts
        
        Args:
            posts: List of post dictionaries
            max_hashtags: Maximum number of hashtags to return
        
        Returns:
            List of generated hashtags
        """
        payload = {"posts": posts, "max_hashtags": max_hashtags}
        
        try:
            response = requests.post(f"{self.base_url}/hashtags", 
                                  json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("hashtags", [])
        except requests.exceptions.RequestException as e:
            return [f"Error: {str(e)}"]
    
    def process_for_hive(self, posts: List[Dict], hive_space_url: str = None) -> Dict:
        """
        Process posts for Hive headline generation
        
        Args:
            posts: List of post dictionaries
            hive_space_url: Optional custom Hive service URL
        
        Returns:
            Hive processing results
        """
        payload = {"posts": posts}
        if hive_space_url:
            payload["hive_space_url"] = hive_space_url
        
        try:
            response = requests.post(f"{self.base_url}/hive/process", 
                                  json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Hive processing failed: {str(e)}"}
    
    def upload_to_hf(self, posts: List[Dict], repo_name: str, hf_token: str = None) -> Dict:
        """
        Upload posts to Hugging Face
        
        Args:
            posts: List of post dictionaries
            repo_name: HF repository name (e.g., 'username/repo')
            hf_token: Hugging Face token (optional, will use env var if not provided)
        
        Returns:
            Upload result
        """
        payload = {
            "posts": posts,
            "repo_name": repo_name,
            "hf_token": hf_token or os.getenv('HF_TOKEN')
        }
        
        try:
            response = requests.post(f"{self.base_url}/upload", 
                                  json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Upload failed: {str(e)}"}
    
    def health_check(self) -> bool:
        """Check if the service is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

# Convenience functions for one-line calls
def scrape_posts(query: str, sources: List[str] = None, limit: int = 100, 
                base_url: str = None) -> Dict:
    """One-line function to scrape posts"""
    api = CollectPostsAPI(base_url)
    return api.scrape(query, sources, limit)

def get_hashtags(posts: List[Dict], max_hashtags: int = 50, 
                base_url: str = None) -> List[str]:
    """One-line function to get hashtags"""
    api = CollectPostsAPI(base_url)
    return api.get_hashtags(posts, max_hashtags)

def process_hive(posts: List[Dict], base_url: str = None) -> Dict:
    """One-line function to process for Hive"""
    api = CollectPostsAPI(base_url)
    return api.process_for_hive(posts)

def upload_hf(posts: List[Dict], repo_name: str, base_url: str = None) -> Dict:
    """One-line function to upload to Hugging Face"""
    api = CollectPostsAPI(base_url)
    return api.upload_to_hf(posts, repo_name)

# Example usage
if __name__ == "__main__":
    # Set your Render service URL
    RENDER_URL = "https://your-app-name.onrender.com"  # Replace with your actual URL
    
    # One-line calls!
    print("🚀 Scraping posts...")
    result = scrape_posts("politics", limit=50, base_url=RENDER_URL)
    
    if "error" not in result:
        posts = result.get("all_posts", [])
        print(f"✅ Found {len(posts)} posts")
        
        # Generate hashtags
        print("🏷️  Generating hashtags...")
        hashtags = get_hashtags(posts, max_hashtags=20, base_url=RENDER_URL)
        print(f"✅ Generated {len(hashtags)} hashtags: {hashtags[:10]}")
        
        # Process for Hive
        print("🐝 Processing for Hive...")
        hive_result = process_hive(posts, base_url=RENDER_URL)
        print(f"✅ Hive processing: {hive_result.get('status', 'Unknown')}")
        
    else:
        print(f"❌ Error: {result['error']}")
