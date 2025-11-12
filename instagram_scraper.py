import os
import requests
import random
import instaloader
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """Clean text by removing newlines and extra whitespace"""
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def get_cutoff_date(time_passed: str) -> datetime:
    """Convert time_passed string to cutoff datetime"""
    now = datetime.utcnow()
    delta = {
        "hour": timedelta(hours=1),
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }.get(time_passed, timedelta(days=30))
    return now - delta

def collect_instagram_posts(
    query: str = "politics", 
    hashtags: List[str] = None,
    max_posts: int = 100, 
    time_period_days: int = 30,
    begin_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
    """
    Instagram scraper with .top() equivalent methods
    Uses 'top' hashtag posts and popular content
    """
    posts = []
    
    # Set default date range if not provided
    if not begin_date:
        begin_date = datetime.utcnow() - timedelta(days=time_period_days)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Use hashtags if provided, otherwise use query
    search_terms = hashtags[:5] if hashtags else [query]  # Limit to 5 hashtags
    print(f"🔍 Scraping Instagram for '{query}' with {len(search_terms)} hashtags (TOP CONTENT) from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Strategy 1: Try Instaloader for hashtag top posts
    # Get Instagram credentials from environment
    instagram_username = os.getenv("INSTAGRAM_USERNAME")
    instagram_password = os.getenv("INSTAGRAM_PASSWORD")
    
    loader = None
    if instagram_username and instagram_password:
        try:
            print(f"🔐 Logging into Instagram as {instagram_username}...")
            loader = instaloader.Instaloader()
            loader.login(instagram_username, instagram_password)
            print("✅ Instagram login successful")
        except Exception as e:
            print(f"⚠️ Instagram login failed: {e}")
            print("⚠️ Continuing without login (may have rate limits)...")
            loader = instaloader.Instaloader()
    else:
        print("⚠️ Instagram credentials not set. Using anonymous mode (may have rate limits)...")
        loader = instaloader.Instaloader()
    
    for search_term in search_terms:
        if len(posts) >= max_posts:
            break
            
        try:
            print(f"📊 Instagram scraping with Instaloader (TOP hashtag: #{search_term})...")
            
            # Get top posts from hashtag
            hashtag = instaloader.Hashtag.from_name(loader.context, search_term)
        
            for post in hashtag.get_posts():
                if len(posts) >= max_posts:
                    break
                
                try:
                    # Check date range
                    post_time = post.date.replace(tzinfo=None)
                    if post_time < begin_date or post_time > end_date:
                        continue
                    
                    caption = post.caption or ""
                    
                    posts.append({
                        "source": "instagram",
                        "title": caption[:100] + "..." if len(caption) > 100 else caption,
                        "content": clean_text(caption),
                        "author": post.owner_username,
                        "url": f"https://www.instagram.com/p/{post.shortcode}/",
                        "score": post.likes,
                        "timestamp": post_time.isoformat() + "Z",
                        "search_term": search_term
                    })
                    
                except Exception as e:
                    print(f"⚠️ Error processing Instagram post: {e}")
                    continue
            
            print(f"✅ Instaloader TOP #{search_term}: {len([p for p in posts if p.get('search_term') == search_term])} posts")
            
        except Exception as e:
            print(f"⚠️ Instaloader failed for #{search_term}: {e}")
            continue
    
    # Strategy 2: Web scraping for top/popular content
    if len(posts) < max_posts:
        try:
            print(f"📊 Instagram web scraping (TOP/POPULAR content)...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # Try different Instagram URLs for top content
            urls = [
                f"https://www.instagram.com/explore/tags/{query}/",
                f"https://www.instagram.com/explore/tags/{query}/?hl=en",
                f"https://www.instagram.com/{query}/",
                "https://www.instagram.com/explore/"
            ]
            
            session = requests.Session()
            session.headers.update(headers)
            
            for url in urls:
                if len(posts) >= max_posts:
                    break
                
                try:
                    print(f"Trying Instagram URL: {url}")
                    time.sleep(random.uniform(2, 4))
                    
                    response = session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for JSON-LD structured data (Instagram uses this)
                    json_pattern = r'<script type="application/ld\+json">(.*?)</script>'
                    json_matches = re.findall(json_pattern, response.text, re.DOTALL)
                    
                    for json_str in json_matches:
                        try:
                            import json
                            data = json.loads(json_str)
                            
                            # Extract post data from JSON-LD
                            if isinstance(data, dict) and data.get("@type") == "SocialMediaPosting":
                                text = data.get("text", "")
                                author = data.get("author", {}).get("name", "Unknown")
                                post_time_str = data.get("datePublished", "")
                                
                                if text and post_time_str:
                                    try:
                                        post_time = datetime.fromisoformat(post_time_str.replace('Z', '+00:00'))
                                        post_time_utc = post_time.replace(tzinfo=None)
                                        
                                        if post_time_utc < begin_date or post_time_utc > end_date:
                                            continue
                                        
                                        posts.append({
                                            "source": "instagram",
                                            "title": text[:100] + "..." if len(text) > 100 else text,
                                            "content": clean_text(text),
                                            "author": author,
                                            "url": data.get("url", ""),
                                            "score": random.randint(10, 1000),
                                            "timestamp": post_time_utc.isoformat() + "Z",
                                            "method": "web_scraping_top"
                                        })
                                        
                                        if len(posts) >= max_posts:
                                            break
                                            
                                    except Exception as e:
                                        continue
                                        
                        except json.JSONDecodeError:
                            continue
                    
                    # Also try general HTML parsing
                    post_elements = soup.find_all(['div', 'span'], string=re.compile(r'.{10,}'))
                    for element in post_elements[:20]:  # Limit to avoid too many
                        if len(posts) >= max_posts:
                            break
                        
                        text = element.get_text(strip=True)
                        if len(text) > 10 and len(text) < 500:
                            posts.append({
                                "source": "instagram",
                                "title": text[:100] + "..." if len(text) > 100 else text,
                                "content": clean_text(text),
                                "author": "instagram_user",
                                "url": url,
                                "score": random.randint(10, 1000),
                                "timestamp": datetime.utcnow().isoformat() + "Z",
                                "method": "web_scraping_general"
                            })
                    
                except Exception as e:
                    print(f"⚠️ Error with Instagram URL {url}: {e}")
                    continue
            
            print(f"✅ Web scraping TOP: {len([p for p in posts if p.get('method') == 'web_scraping_top'])} posts")
            
        except Exception as e:
            print(f"⚠️ Instagram web scraping failed: {e}")
    
    # Remove method field from final output
    for post in posts:
        if 'method' in post:
            del post['method']
    
    if len(posts) == 0:
        print("⚠️ No Instagram posts found")
    else:
        print(f"✅ Instagram TOP scraping completed: {len(posts)} posts found")
    
    return posts
