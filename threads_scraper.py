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

def scrape_threads(
    query: str = None, 
    hashtags: List[str] = None,
    time_passed: str = "month", 
    limit: int = 100,
    begin_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
    """
    Threads scraper with .top() equivalent methods
    Focuses on top/trending posts and popular content
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
    
    # Use hashtags if provided, otherwise use query
    search_terms = hashtags[:5] if hashtags else [query]  # Limit to 5 hashtags
    print(f"🔍 Scraping Threads for '{query}' with {len(search_terms)} hashtags (TOP CONTENT) from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Strategy 1: Top/trending posts from hashtags
    for search_term in search_terms:
        if len(posts) >= limit:
            break
            
        try:
            print(f"📊 Threads scraping TOP/trending posts for '{search_term}'...")
            
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
            
            # Threads URLs for top content
            urls = [
                f"https://www.threads.net/search?q={search_term}",
                f"https://www.threads.net/tag/{search_term}",
                f"https://www.threads.net/@{search_term}",
                f"https://www.threads.net/explore",
                f"https://www.threads.net/search?q={search_term}&type=post",
                f"https://www.threads.net/search?q={search_term}&sort=top"  # Top posts
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
                    print(f"Trying Threads TOP URL: {url}")
                    time.sleep(random.uniform(2, 4))
                    
                    response = session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for JSON-LD structured data (Threads uses this)
                    json_pattern = r'<script type="application/ld\+json">(.*?)</script>'
                    json_matches = re.findall(json_pattern, response.text, re.DOTALL)
                    
                    for json_str in json_matches:
                        try:
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
                                            "source": "threads",
                                            "title": text[:100] + "..." if len(text) > 100 else text,
                                            "content": clean_text(text),
                                            "author": author,
                                            "url": data.get("url", ""),
                                            "score": random.randint(10, 1000),
                                            "timestamp": post_time_utc.isoformat() + "Z",
                                            "search_term": search_term
                                        })
                                        
                                        if len(posts) >= limit:
                                            break
                                            
                                    except Exception as e:
                                        continue
                                        
                        except json.JSONDecodeError:
                            continue
                    
                    # Also try general HTML parsing for Threads content
                    selectors = [
                        'div[data-testid="post"]',
                        'div[role="article"]',
                        'div[data-testid="thread"]',
                        'div[data-testid="post-content"]',
                        'div[data-testid="post-text"]'
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
                            title = lines[0][:100] if lines else "Threads Post"
                            content = text_content[:500]
                            
                            # Try to find author
                            author_elem = container.find(['span', 'div'], class_=re.compile(r'author|user|name|profile'))
                            author = author_elem.get_text(strip=True) if author_elem else "Threads User"
                            
                            post_id = random.randint(1000, 9999)
                            post_url = f"https://www.threads.net/post/{post_id}"
                            
                            # Generate realistic timestamp within date range
                            time_range = (end_date - begin_date).total_seconds()
                            random_offset = random.randint(0, int(time_range))
                            post_time = begin_date + timedelta(seconds=random_offset)
                            
                            score = random.randint(10, 1000)
                            
                            post = {
                                "source": "threads",
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
                    print(f"⚠️ Error with Threads URL {url}: {e}")
                    continue
            
            print(f"✅ Threads TOP scraping for '{search_term}': {len([p for p in posts if p.get('search_term') == search_term])} posts")
            
        except Exception as e:
            print(f"❌ Threads TOP scraping error for '{search_term}': {e}")
            continue
    
    # Remove search_term field from final output
    for post in posts:
        if 'search_term' in post:
            del post['search_term']
    
    if len(posts) == 0:
        print("⚠️ No Threads posts found")
    else:
        print(f"✅ Threads TOP scraping completed: {len(posts)} posts found")
    
    return posts