import os
import requests
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"


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
        if api_key and api_key != "YOUR_YOUTUBE_API_KEY":
            try:
                max_per_request = 50
                total_requests = (max_results + max_per_request - 1) // max_per_request
                next_page_token = None

                # define UTC cutoff for filtering
                cutoff_dt = datetime.now(timezone.utc) - timedelta(days=time_period_days)

                for request_num in range(total_requests):
                    if len(posts) >= max_results:
                        break
                        
                    url = "https://www.googleapis.com/youtube/v3/search"
                    published_after = (datetime.now(timezone.utc) - timedelta(days=time_period_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

                    params = {
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": min(max_per_request, max_results - len(posts)),
                        "key": api_key,
                        "order": "date",  # <-- changed from relevance to date
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
                        
                        video_id = item["id"].get("videoId")
                        if not video_id:
                            continue
                        
                        title = item["snippet"]["title"]
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        content = item["snippet"].get("description", "")
                        published_str = item["snippet"].get("publishedAt", "")
                        
                        # 🧩 pub_s section (cutoff filtering)
                        try:
                            pub_dt = datetime.strptime(published_str, ISO8601).replace(tzinfo=timezone.utc)
                        except Exception:
                            continue  # skip if invalid timestamp

                        # skip posts older than cutoff_dt
                        if pub_dt < cutoff_dt:
                            continue
                        
                        posts.append({
                            "source": "YouTube",
                            "title": clean_text(title),
                            "content": clean_text(content),
                            "author": item["snippet"]["channelTitle"],
                            "url": url,
                            "score": random.randint(100, 10000),
                            "created_utc": published_str
                        })
            except Exception as e:
                print(f"YouTube API error: {e}")
        
        if len(posts) == 0:
            print("YouTube API key not valid or no results found within time window.")
            
    except Exception as e:
        print(f"YouTube error: {e}")
        print(f"YouTube scraping completed: {len(posts)} posts found (failed)")
    
    return posts
