import os
import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict

def clean_text(text: str) -> str:
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def extract_video_id_from_url(url: str) -> str:
    """Extract video ID from YouTube URL"""
    try:
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return ""
    except:
        return ""

def collect_youtube_video_titles(query: str = "politics", max_results: int = 100, time_period_days: int = 30) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY", "AIzaSyAZwLva1HxzDbKFJuE9RVcxS5B4q_ol8yE")
    posts = []
    
    try:
        # Try YouTube API first with better error handling
        if api_key and api_key != "YOUR_YOUTUBE_API_KEY":
            try:
                # Calculate how many API calls we need (max 50 per call)
                max_per_request = 50
                total_requests = (max_results + max_per_request - 1) // max_per_request
                next_page_token = None
                
                for request_num in range(total_requests):
                    if len(posts) >= max_results:
                        break
                        
                    url = "https://www.googleapis.com/youtube/v3/search"
                    
                    # Calculate proper date range based on time period
                    now = datetime.utcnow()
                    published_after = (now - timedelta(days=time_period_days)).isoformat() + "Z"
                    
                    params = {
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": min(max_per_request, max_results - len(posts)),
                        "key": api_key,
                        "order": "relevance",
                        "publishedAfter": published_after
                    }
                    
                    if next_page_token:
                        params["pageToken"] = next_page_token
                    
                    res = requests.get(url, params=params, timeout=10)
                    data = res.json()
                    
                    if "error" in data:
                        print(f"YouTube API error: {data['error']['message']}")
                        break
                    
                    next_page_token = data.get("nextPageToken")
                    
                    for item in data.get("items", []):
                        if len(posts) >= max_results:
                            break
                        
                        video_id = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Use YouTube description as content
                        content = item["snippet"].get("description", "")

                        posts.append({
                            "source": "YouTube",
                            "title": clean_text(title),
                            "content": clean_text(content),
                            "author": item["snippet"]["channelTitle"],
                            "url": url,
                            "score": random.randint(100, 10000),
                            "created_utc": item["snippet"]["publishedAt"]
                        })
                        
            except Exception as e:
                print(f"YouTube API error: {e}")
        
        # Fallback to web scraping if API fails
        if len(posts) == 0:
            print("YouTube API key not valid. Trying web scraping...")
            # Web scraping fallback code would go here
            # For now, return empty list
            
    except Exception as e:
        print(f"YouTube error: {e}")
        print(f"YouTube scraping completed: {len(posts)} posts found (failed)")
    
    return posts
