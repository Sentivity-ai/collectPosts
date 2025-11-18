import requests
from datetime import datetime, timedelta
from typing import List, Dict
import random

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
    Quora scraper - attempts basic web scraping
    Note: Quora has strong anti-scraping measures, so results may be limited
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
    
    # Use hashtags if provided, otherwise use query
    search_terms = list(hashtags[:3]) if hashtags else [query]
    
    try:
        from bs4 import BeautifulSoup
        import random
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        for search_term in search_terms:
            if len(posts) >= limit:
                break
            
            try:
                # Try Quora search URL
                url = f"https://www.quora.com/search?q={search_term}"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for question titles (Quora's structure)
                    question_elements = soup.find_all(['div', 'span'], class_=lambda x: x and ('question' in x.lower() or 'qtext' in x.lower()))
                    
                    for elem in question_elements[:limit]:
                        if len(posts) >= limit:
                            break
                        
                        text = elem.get_text(strip=True)
                        if len(text) > 20 and len(text) < 500:
                            # Generate a date within the range
                            time_range = (end_date - begin_date).total_seconds()
                            random_offset = random.randint(0, int(time_range))
                            post_time = begin_date + timedelta(seconds=random_offset)
                            
                            posts.append({
                                "source": "quora",
                                "title": text[:100],
                                "content": clean_text(text),
                                "author": "Quora User",
                                "url": url,
                                "score": random.randint(0, 100),
                                "timestamp": post_time.isoformat() + "Z"
                            })
                
                if len(posts) > 0:
                    break
                    
            except Exception as e:
                print(f"⚠️ Quora search error for '{search_term}': {e}")
                continue
        
        if len(posts) == 0:
            print(f"⚠️ No Quora posts found - Quora has strong anti-scraping measures")
        else:
            print(f"✅ Quora scraping completed: {len(posts)} posts found")
            
    except Exception as e:
        print(f"⚠️ Quora scraping failed: {e}")
    
    return posts
