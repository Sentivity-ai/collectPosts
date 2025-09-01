import requests
import json
import os
from typing import List, Dict
from datetime import datetime

class CollectPostsAPI:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('COLLECTPOSTS_URL', 'http://localhost:8000')
        if not self.base_url.startswith('http'):
            self.base_url = f'https://{self.base_url}'
    
    def scrape(self, query: str, sources: List[str] = None, limit: int = 100, days: int = 30) -> Dict:
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
        payload = {"posts": posts, "max_hashtags": max_hashtags}
        
        try:
            response = requests.post(f"{self.base_url}/hashtags", 
                                  json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("hashtags", [])
        except requests.exceptions.RequestException as e:
            return [f"Error: {str(e)}"]
    
    def process_for_hive(self, posts: List[Dict], hive_space_url: str = None) -> Dict:
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
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

def scrape_posts(query: str, sources: List[str] = None, limit: int = 100, 
                base_url: str = None) -> Dict:
    api = CollectPostsAPI(base_url)
    return api.scrape(query, sources, limit)

def get_hashtags(posts: List[Dict], max_hashtags: int = 50, 
                base_url: str = None) -> List[str]:
    api = CollectPostsAPI(base_url)
    return api.get_hashtags(posts, max_hashtags)

def process_hive(posts: List[Dict], base_url: str = None) -> Dict:
    api = CollectPostsAPI(base_url)
    return api.process_for_hive(posts)

def upload_hf(posts: List[Dict], repo_name: str, base_url: str = None) -> Dict:
    api = CollectPostsAPI(base_url)
    return api.upload_to_hf(posts, repo_name)

if __name__ == "__main__":
    RENDER_URL = "https://your-app-name.onrender.com"
    
    result = scrape_posts("politics", limit=50, base_url=RENDER_URL)
    
    if "error" not in result:
        posts = result.get("all_posts", [])
        print(f"Found {len(posts)} posts")
        
        hashtags = get_hashtags(posts, max_hashtags=20, base_url=RENDER_URL)
        print(f"Generated {len(hashtags)} hashtags: {hashtags[:10]}")
        
        hive_result = process_hive(posts, base_url=RENDER_URL)
        print(f"Hive processing: {hive_result.get('status', 'Unknown')}")
        
    else:
        print(f"Error: {result['error']}")
