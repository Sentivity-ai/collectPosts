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

def scrape_threads(
    query: str = None, 
    hashtags: List[str] = None,
    time_passed: str = "month", 
    limit: int = 100,
    begin_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
    """
    Threads scraper - attempts basic web scraping
    Note: Threads requires authentication, so results may be limited
    """
    posts = []
    
    if not query:
        print("❌ Threads scraping: No query provided")
        return []
    
    # Set default date range if not provided
    if not begin_date:
        begin_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    print(f"🔍 Scraping Threads for '{query}' from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Use hashtags if provided, otherwise use query
    search_terms = list(hashtags[:3]) if hashtags else [query]
    
    for term in search_terms:
        if len(posts) >= limit:
            break
        remaining = limit - len(posts)
        print(f"📊 DuckDuckGo fallback for Threads term '{term}'...")
        posts.extend(
            search_site_posts(
                site="www.threads.net",
                query=term,
                limit=remaining,
                begin_date=begin_date,
                end_date=end_date,
                source="threads",
            )
        )
    
    if len(posts) == 0:
        print("⚠️ No Threads posts found via search fallback")
    else:
        print(f"✅ Threads search fallback returned {len(posts)} posts")
    
    return posts
