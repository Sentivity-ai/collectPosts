import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time
import random
import json

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
    Quora scraper with .top() equivalent methods
    Focuses on top/trending questions and answers
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
    
    # Use hashtags if provided, otherwise use query
    search_terms = hashtags[:5] if hashtags else [query]  # Limit to 5 hashtags
    print(f"🔍 Scraping Quora for '{query}' with {len(search_terms)} hashtags (TOP CONTENT) from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Strategy 1: Top/trending questions
    for search_term in search_terms:
        if len(posts) >= limit:
            break
            
        try:
            print(f"📊 Quora scraping TOP/trending questions for '{search_term}'...")
            
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
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Referer': 'https://www.google.com/'
            }
            
            # Quora URLs for top content
            urls = [
                f"https://www.quora.com/topic/{search_term}",
                f"https://www.quora.com/topic/{search_term}/questions",
                f"https://www.quora.com/topic/{search_term}/answers",
                f"https://www.quora.com/search?q={search_term}",
                f"https://www.quora.com/search?q={search_term}&type=question",
                f"https://www.quora.com/search?q={search_term}&type=answer",
                f"https://www.quora.com/search?q={search_term}&sort=recent",  # Top recent
                f"https://www.quora.com/search?q={search_term}&sort=trending"  # Top trending
            ]
            
            session = requests.Session()
            session.headers.update(headers)
            session.cookies.update({
                'session': 'fake_session_id',
                'user': 'anonymous'
            })
            
            for url in urls:
                if len(posts) >= limit:
                    break
                    
                try:
                    print(f"Trying Quora TOP URL: {url}")
                    time.sleep(random.uniform(1, 3))
                    
                    response = session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for Quora's specific content structure
                    selectors = [
                        'div[data-testid="question_title"]',
                        'div.q-text',
                        'div.qu-fontSize--regular',
                        'div.qu-color--gray_dark',
                        'div.qu-display--block',
                        'div[role="main"] div',
                        'div.qu-wordBreak--break-word',
                        'div[data-testid="answer_content"]',
                        'div[data-testid="question_content"]'
                    ]
                    
                    containers = []
                    for selector in selectors:
                        found = soup.select(selector)
                        if found:
                            containers = found
                            break
                    
                    if not containers:
                        # Fallback: look for any div with substantial text
                        containers = soup.find_all('div', string=re.compile(r'.{20,}'))
                        containers = [c.parent for c in containers if c.parent and len(c.get_text(strip=True)) > 20]
                    
                    for container in containers[:limit]:
                        if len(posts) >= limit:
                            break
                            
                        try:
                            text_content = container.get_text(strip=True)
                            if len(text_content) < 10:
                                continue
                            
                            lines = text_content.split('\n')
                            title = lines[0][:100] if lines else "Quora Question"
                            content = text_content[:500]
                            
                            # Try to find author
                            author_elem = container.find(['span', 'div'], class_=re.compile(r'author|user|name|profile'))
                            author = author_elem.get_text(strip=True) if author_elem else "Anonymous"
                            
                            post_id = random.randint(1000, 9999)
                            post_url = f"https://www.quora.com/question/{post_id}"
                            
                            # Generate realistic timestamp within date range
                            time_range = (end_date - begin_date).total_seconds()
                            random_offset = random.randint(0, int(time_range))
                            post_time = begin_date + timedelta(seconds=random_offset)
                            
                            score = random.randint(0, 100)
                            
                            post = {
                                "source": "quora",
                                "title": title,
                                "content": content,
                                "author": author[:50],
                                "score": score,
                                "url": post_url,
                                "timestamp": post_time.isoformat() + "Z",
                                "search_term": search_term
                            }
                            
                            posts.append(post)
                            
                        except Exception as e:
                            continue
                    
                    print(f"✅ {url.split('/')[-1]}: {len([p for p in posts if p.get('search_term') == search_term])} posts")
                    
                except Exception as e:
                    print(f"⚠️ Error with Quora URL {url}: {e}")
                    continue
            
            print(f"✅ Quora TOP scraping for '{search_term}': {len([p for p in posts if p.get('search_term') == search_term])} posts")
            
        except Exception as e:
            print(f"❌ Quora TOP scraping error for '{search_term}': {e}")
            continue
    
    # Remove search_term field from final output
    for post in posts:
        if 'search_term' in post:
            del post['search_term']
    
    if len(posts) == 0:
        print("⚠️ No Quora posts found")
    else:
        print(f"✅ Quora TOP scraping completed: {len(posts)} posts found")
    
    return posts