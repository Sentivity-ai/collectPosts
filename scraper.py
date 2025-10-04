from typing import List, Dict
from scrapers import (
    collect_reddit_posts,
    collect_youtube_video_titles,
    collect_instagram_posts,
    collect_quora_posts
)

def scrape_posts(sources: List[str], query: str, time_passed: str = "week", limit: int = 100) -> List[Dict]:
    """
    Main scraping function that coordinates all platform scrapers
    
    Args:
        sources: List of platforms to scrape from ['reddit', 'youtube', 'instagram', 'quora']
        query: Search term or subreddit name
        time_passed: Time period ('day', 'week', 'month', 'year')
        limit: Maximum posts per source
    
    Returns:
        List of post dictionaries from all sources
    """
    all_posts = []
    
    # Convert time_passed to days
    time_mapping = {
        "hour": 1,
        "day": 1, 
        "week": 7,
        "month": 30,
        "year": 365
    }
    days = time_mapping.get(time_passed, 7)
    
    # Scrape from each requested source
    for source in sources:
        try:
            if source.lower() == "reddit":
                posts = collect_reddit_posts(query, days, limit)
                all_posts.extend(posts)
                print(f"Reddit scraping completed: {len(posts)} posts found (real data)")
                
            elif source.lower() == "youtube":
                posts = collect_youtube_video_titles(query, limit, days)
                all_posts.extend(posts)
                print(f"YouTube scraping completed: {len(posts)} posts found (real data)")
                
            elif source.lower() == "instagram":
                posts = collect_instagram_posts(query, limit, days)
                all_posts.extend(posts)
                print(f"Instagram scraping completed: {len(posts)} posts found (real data)")
                
            elif source.lower() == "quora":
                posts = collect_quora_posts(query, days, limit)
                all_posts.extend(posts)
                print(f"Quora scraping completed: {len(posts)} posts found (real data)")
                
        except Exception as e:
            print(f"Error scraping {source}: {e}")
    
    return all_posts
