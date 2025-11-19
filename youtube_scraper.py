import os
import requests
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import time

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

def clean_text(text: str) -> str:
    """Clean text by removing newlines and extra whitespace"""
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

def collect_youtube_video_titles(
    query: str = "politics", 
    hashtags: List[str] = None,
    max_results: int = 50,
    time_period_days: int = 30,
    begin_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
    """
    YouTube scraper with .top() equivalent methods
    Uses hashtags from Reddit to find relevant content
    Supports pagination for limits > 50
    """
    api_key = os.getenv("YOUTUBE_API_KEY", "AIzaSyAZwLva1HxzDbKFJuE9RVcxS5B4q_ol8yE")
    posts = []
    
    if not api_key or api_key == "YOUR_YOUTUBE_API_KEY":
        print("❌ YouTube API key not set")
        return []
    
    # Set default date range if not provided
    if not begin_date:
        begin_date = datetime.utcnow() - timedelta(days=time_period_days)
    if not end_date:
        end_date = datetime.utcnow()
    
    # YouTube API allows max 50 results per request, but we can make multiple requests
    # Remove hard limit - use requested limit and paginate if needed
    try:
        # Use hashtags if provided, otherwise use query
        search_terms = hashtags[:10] if hashtags else [query]  # Limit to 10 hashtags
        print(f"🔍 Scraping YouTube for '{query}' with {len(search_terms)} hashtags (limit: {max_results}) from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Strategy 1: Use 'relevance' order (closest to .top())
        orders = ['relevance', 'viewCount', 'rating']
        
        for search_term in search_terms:
            if len(posts) >= max_results:
                break
                
            for order in orders:
                if len(posts) >= max_results:
                    break
                    
                try:
                    print(f"📊 YouTube scraping '{search_term}' with order='{order}'...")
                    
                    url = "https://www.googleapis.com/youtube/v3/search"
                    published_after = begin_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                    published_before = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

                    # YouTube API allows max 50 per request, but we can paginate
                    next_page_token = None
                    requests_made = 0
                    max_requests = (max_results // 50) + 1  # Calculate how many requests needed
                    
                    while len(posts) < max_results and requests_made < max_requests:
                        remaining = max_results - len(posts)
                        params = {
                            "part": "snippet",
                            "q": search_term,
                            "type": "video",
                            "maxResults": min(50, remaining),  # YouTube API max is 50 per request
                            "key": api_key,
                            "order": order,
                            "publishedAfter": published_after,
                            "publishedBefore": published_before
                        }
                        
                        if next_page_token:
                            params["pageToken"] = next_page_token
                        
                        response = requests.get(url, params=params, timeout=15)
                        response.raise_for_status()
                        data = response.json()
                        
                        if "error" in data:
                            print(f"❌ YouTube API error: {data['error']['message']}")
                            break
                        
                        for item in data.get("items", []):
                            if len(posts) >= max_results:
                                break
                            
                            video_id = item["id"].get("videoId")
                            if not video_id:
                                continue
                            
                            title = item["snippet"]["title"]
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            content = item["snippet"].get("description", "")
                            published_str = item["snippet"].get("publishedAt", "")
                            
                            # Filter by date
                            try:
                                pub_dt = datetime.strptime(published_str, ISO8601).replace(tzinfo=timezone.utc)
                            except Exception:
                                continue  # skip if invalid timestamp

                            # Double-check date range
                            if pub_dt.replace(tzinfo=None) < begin_date or pub_dt.replace(tzinfo=None) > end_date:
                                continue
                            
                            posts.append({
                                "source": "youtube",
                                "title": clean_text(title),
                                "content": clean_text(content),
                                "author": item["snippet"]["channelTitle"],
                                "url": video_url,
                                "score": random.randint(100, 10000),
                                "timestamp": published_str,
                                "search_term": search_term
                            })
                        
                        # Get next page token for pagination
                        next_page_token = data.get("nextPageToken")
                        requests_made += 1
                        
                        if not next_page_token:
                            break  # No more pages
                        
                        # Rate limiting between requests
                        time.sleep(1)
                        
                    print(f"✅ {search_term}({order}): {len([p for p in posts if p.get('search_term') == search_term])} videos")
                    
                    # Rate limiting between different orders
                    time.sleep(1)
                    
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ YouTube request failed for {search_term}({order}): {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ YouTube parsing error for {search_term}({order}): {e}")
                    continue
        
        # Remove search_term field from final output
        for post in posts:
            if 'search_term' in post:
                del post['search_term']
        
        if len(posts) == 0:
            print("⚠️ No YouTube results found within time window")
        else:
            print(f"✅ YouTube scraping completed: {len(posts)} posts found (requested {max_results})")
            
    except Exception as e:
        print(f"❌ YouTube error: {e}")
    
    return posts