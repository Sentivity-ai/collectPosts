import os
import praw
from datetime import datetime, timedelta
from typing import List, Dict

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID", "F9rgR81aVwJSjyB0cfqzLQ"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET", "jW9w9dSkntRzjlo2_S_HKRxaiSFgVw"),
    user_agent="sentivityb2c/0.1"
)

def clean_text(text: str) -> str:
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def collect_reddit_posts(subreddit_name: str = "politics", time_period_days: int = 30, limit: int = 100) -> List[Dict]:
    posts = []
    try:
        # Try multiple Reddit API approaches
        try:
            subreddit = reddit.subreddit(subreddit_name)
            cutoff = (datetime.utcnow() - timedelta(days=time_period_days)).timestamp()
            
            # Map days to Reddit time filters
            time_filter_map = {
                1: 'day',
                7: 'week', 
                30: 'month',
                365: 'year',
                3650: 'all'  # 10 years
            }
            reddit_time_filter = time_filter_map.get(time_period_days, 'week')
            
            # Try different sorting methods with proper time filtering
            sorting_methods = [
                ('hot', subreddit.hot(limit=limit)),
                ('top', subreddit.top(time_filter=reddit_time_filter, limit=limit)),
                ('new', subreddit.new(limit=limit)),
                ('rising', subreddit.rising(limit=limit))
            ]
            
            for sort_method, post_generator in sorting_methods:
                try:
                    for post in post_generator:
                        if len(posts) >= limit:
                            break
                        
                        # Check if post is within time period
                        if hasattr(post, 'created_utc') and post.created_utc < cutoff:
                            continue
                            
                        posts.append({
                            "source": "Reddit",
                            "title": clean_text(post.title),
                            "content": clean_text(post.selftext),
                            "author": str(post.author),
                            "url": f"https://reddit.com{post.permalink}",
                            "score": post.score,
                            "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"Error with {sort_method} sorting: {e}")
                    continue
                    
        except Exception as e:
            print(f"Reddit API error: {e}")
            
    except Exception as e:
        print(f"Reddit scraping error: {e}")
    
    return posts
