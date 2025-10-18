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

def collect_reddit_posts(
    subreddit_name: str = "politics",
    time_period_days: int = 30,
    limit: int = 100000,
    fetch_multiplier: int = 5,   # fetch extra to allow filtering
) -> List[Dict]:

    posts: List[Dict] = []
    seen_ids = set()

    cutoff_dt = datetime.utcnow() - timedelta(days=time_period_days)
    cutoff_ts = cutoff_dt.timestamp()

    try:
        subreddit = reddit.subreddit(subreddit_name)

        # 1) Chronological pass (preferred)
        # Fetch more than `limit` so we can filter by time and still return up to `limit`.
        fetch_limit = min(1000, max(limit * fetch_multiplier, limit))
        for post in subreddit.top(limit=fetch_limit):
            # `new()` is newest->oldest, so we can break once older than cutoff
            if getattr(post, "created_utc", 0) < cutoff_ts:
                break
            if post.id in seen_ids:
                continue
            seen_ids.add(post.id)

            posts.append({
                "source": "Reddit",
                "title": clean_text(getattr(post, "title", "")),
                "content": clean_text(getattr(post, "selftext", "")),
                "author": (post.author.name if getattr(post, "author", None) else "[deleted]"),
                "url": f"https://reddit.com{getattr(post, 'permalink', '')}",
                "score": getattr(post, "score", 0),
                "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                "id": post.id,
            })
            if len(posts) >= limit:
                break

        # 2) Optional fallback if nothing found in the strict window
        if not posts:
            for post in subreddit.top(limit=min(5000, fetch_limit)):
                if getattr(post, "created_utc", 0) < cutoff_ts:
                    continue
                if post.id in seen_ids:
                    continue
                seen_ids.add(post.id)
                posts.append({
                    "source": "Reddit",
                    "title": clean_text(getattr(post, "title", "")),
                    "content": clean_text(getattr(post, "selftext", "")),
                    "author": (post.author.name if getattr(post, "author", None) else "[deleted]"),
                    "url": f"https://reddit.com{getattr(post, 'permalink', '')}",
                    "score": getattr(post, "score", 0),
                    "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "id": post.id,
                })
                if len(posts) >= limit:
                    break

    except Exception as e:
        print(f"Reddit scraping error: {e}")

    # Return up to `limit` (already time-filtered)
    return posts[:limit]
