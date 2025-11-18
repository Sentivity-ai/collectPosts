import os
import random
import instaloader
from datetime import datetime, timedelta
from typing import List, Dict

from site_search_utils import search_site_posts

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
    seen_urls = set()
    
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
            # Try to load session if it exists
            try:
                loader.load_session_from_file(instagram_username)
                print("✅ Loaded existing Instagram session")
            except:
                # If no session, login
                loader.login(instagram_username, instagram_password)
                # Save session for future use
                loader.save_session_to_file()
                print("✅ Instagram login successful and session saved")
        except Exception as e:
            print(f"⚠️ Instagram login failed: {e}")
            print("⚠️ Continuing without login (may have rate limits)...")
            loader = instaloader.Instaloader()
    else:
        print("⚠️ Instagram credentials not set. Using anonymous mode (may have rate limits)...")
        print("⚠️ Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables for better results")
        loader = instaloader.Instaloader()
    
    for search_term in search_terms:
        if len(posts) >= max_posts:
            break
            
        try:
            print(f"📊 Instagram scraping with Instaloader (TOP hashtag: #{search_term})...")
            
            # Get top posts from hashtag (limit to avoid too much scraping)
            hashtag = instaloader.Hashtag.from_name(loader.context, search_term)
        
            # Limit posts to check to avoid long scraping
            post_count = 0
            max_check = min(max_posts * 3, 100)  # Check 3x limit or max 100 posts
            
            for post in hashtag.get_posts():
                post_count += 1
                if post_count > max_check:
                    break
                if len(posts) >= max_posts:
                    break
                
                try:
                    # Check date range
                    post_time = post.date.replace(tzinfo=None)
                    if post_time < begin_date or post_time > end_date:
                        continue
                    
                    caption = post.caption or ""
                    
                    new_post = {
                        "source": "instagram",
                        "title": caption[:100] + "..." if len(caption) > 100 else caption,
                        "content": clean_text(caption),
                        "author": post.owner_username,
                        "url": f"https://www.instagram.com/p/{post.shortcode}/",
                        "score": post.likes,
                        "timestamp": post_time.isoformat() + "Z",
                        "search_term": search_term
                    }

                    if new_post["url"] in seen_urls:
                        continue
                    seen_urls.add(new_post["url"])
                    posts.append(new_post)
                    
                except Exception as e:
                    print(f"⚠️ Error processing Instagram post: {e}")
                    continue
            
            print(f"✅ Instaloader TOP #{search_term}: {len([p for p in posts if p.get('search_term') == search_term])} posts")
            
        except Exception as e:
            print(f"⚠️ Instaloader failed for #{search_term}: {e}")
            continue
    
    # Strategy 2: Lightweight DuckDuckGo fallback
    if len(posts) < max_posts:
        remaining_total = max_posts - len(posts)
        print(f"📊 DuckDuckGo fallback for Instagram (remaining {remaining_total} posts)...")
        for term in search_terms:
            if remaining_total <= 0:
                break
            fallback_posts = search_site_posts(
                site="www.instagram.com",
                query=term,
                limit=remaining_total,
                begin_date=begin_date,
                end_date=end_date,
                source="instagram",
            )
            for fp in fallback_posts:
                if fp["url"] in seen_urls:
                    continue
                seen_urls.add(fp["url"])
                posts.append(fp)
            remaining_total = max_posts - len(posts)
    
    if len(posts) == 0:
        print("⚠️ No Instagram posts found")
    else:
        print(f"✅ Instagram TOP scraping completed: {len(posts)} posts found")
    
    return posts
