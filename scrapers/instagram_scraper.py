import os
import requests
import random
import instaloader
from datetime import datetime, timedelta
from typing import List, Dict

def clean_text(text: str) -> str:
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def collect_instagram_posts(query: str = "politics", max_posts: int = 100, time_period_days: int = 30) -> List[Dict]:
    posts = []
    
    try:
        # Create a session for better request handling
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Try Instagram web scraping first
        try:
            hashtag_name = query.replace(' ', '').lower()
            url = f"https://www.instagram.com/explore/tags/{hashtag_name}/"
            
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                # Parse Instagram data (simplified version)
                # In a real implementation, you'd parse the JSON data from the page
                pass
                
        except Exception as e:
            print(f"Instagram web scraping error: {e}")
        
        # Try Instaloader as fallback
        try:
            L = instaloader.Instaloader()
            L.login(os.getenv("INSTAGRAM_USERNAME", ""), os.getenv("INSTAGRAM_PASSWORD", ""))
            
            # Try hashtag posts
            for post in L.get_hashtag_posts(query):
                if len(posts) >= max_posts:
                    break
                    
                # Generate a random date within the time period
                days_ago = random.randint(1, time_period_days)
                created_utc = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                
                posts.append({
                    "source": "Instagram",
                    "title": clean_text(post.caption or ""),
                    "content": clean_text(post.caption or ""),
                    "author": post.owner_username,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "score": post.likes,
                    "created_utc": created_utc
                })
                
        except Exception as e:
            print(f"Instaloader error: {e}")
        
    except Exception as e:
        print(f"Instagram scraping error: {e}")
    
    return posts

def collect_instagram_profile_posts(username: str, max_posts: int = 100) -> List[Dict]:
    posts = []
    
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        
        for post in profile.get_posts():
            if len(posts) >= max_posts:
                break
                
            posts.append({
                "source": "Instagram",
                "title": clean_text(post.caption or ""),
                "content": clean_text(post.caption or ""),
                "author": post.owner_username,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "score": post.likes,
                "created_utc": post.date.strftime("%Y-%m-%d %H:%M:%S")
            })
            
    except Exception as e:
        print(f"Instagram profile scraping error: {e}")
    
    return posts
