import requests
from datetime import datetime, timedelta
from typing import List, Dict

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

def scrape_quora(
    query: str = None, 
    hashtags: List[str] = None,
    time_passed: str = "month", 
    limit: int = 100,
    begin_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
    """
    Quora scraper - simplified to avoid slow HTML scraping
    Quora requires authentication and blocks web scraping, so returns empty
    """
    posts = []
    
    if not query:
        print("❌ Quora scraping: No query provided")
        return []
    
    # Set default date range if not provided
    if not begin_date:
        begin_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    print(f"🔍 Scraping Quora for '{query}' from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"⚠️ Quora scraping skipped - requires authentication and web scraping is too slow/unreliable")
    print(f"⚠️ Quora API not available. Returning empty results.")
    
    return posts
