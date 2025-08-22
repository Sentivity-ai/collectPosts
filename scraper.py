import os
import praw
import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict
import instaloader
import time
import random

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
        subreddit = reddit.subreddit(subreddit_name)
        cutoff = (datetime.utcnow() - timedelta(days=time_period_days)).timestamp()
        
        for post in subreddit.top(time_filter='month', limit=limit):
            if post.created_utc >= cutoff:
                posts.append({
                    "source": "Reddit",
                    "title": clean_text(post.title),
                    "content": clean_text(post.selftext),
                    "author": post.author.name if post.author else "[deleted]",
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        print(f"Reddit error: {e}")
        raise e
    
    return posts

def collect_quora_posts(query: str = "politics", max_pages: int = 3, limit: int = None) -> List[Dict]:
    posts = []
    
    mock_quora_questions = [
        {
            "title": f"What are the best practices for {query}?",
            "content": f"Looking for tips and best practices for {query}. What should I know?",
            "url": f"https://quora.com/What-are-the-best-practices-for-{query.replace(' ', '-')}",
            "score": "15 answers"
        },
        {
            "title": f"How to get started with {query}?",
            "content": f"I'm a beginner and want to learn {query}. Where should I start?",
            "url": f"https://quora.com/How-to-get-started-with-{query.replace(' ', '-')}",
            "score": "23 answers"
        },
        {
            "title": f"What are the common mistakes in {query}?",
            "content": f"What mistakes should I avoid when learning {query}?",
            "url": f"https://quora.com/What-are-the-common-mistakes-in-{query.replace(' ', '-')}",
            "score": "8 answers"
        },
        {
            "title": f"Which resources are best for learning {query}?",
            "content": f"Can anyone recommend good resources for learning {query}?",
            "url": f"https://quora.com/Which-resources-are-best-for-learning-{query.replace(' ', '-')}",
            "score": "12 answers"
        },
        {
            "title": f"What is the future of {query}?",
            "content": f"How do you see {query} evolving in the next few years?",
            "url": f"https://quora.com/What-is-the-future-of-{query.replace(' ', '-')}",
            "score": "6 answers"
        }
    ]
    
    max_posts = limit if limit else max_pages * 2
    for i, mock_question in enumerate(mock_quora_questions[:max_posts]):
        posts.append({
            "source": "Quora",
            "title": clean_text(mock_question["title"]),
            "content": clean_text(mock_question["content"]),
            "author": f"QuoraUser{i+1}",
            "url": mock_question["url"],
            "score": mock_question["score"],
            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    print(f"Quora scraping completed: {len(posts)} posts found (mock data)")
    return posts

def collect_youtube_video_titles(query: str = "politics", max_results: int = 10) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
    posts = []
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": api_key
        }
        
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        
        if "error" in data:
            raise Exception(f"YouTube API error: {data['error'].get('message', 'Unknown error')}")
        
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            posts.append({
                "source": "YouTube",
                "title": clean_text(title),
                "content": "",
                "author": item["snippet"]["channelTitle"],
                "url": url,
                "score": "",
                "created_utc": item["snippet"]["publishedAt"]
            })
    except Exception as e:
        print(f"YouTube error: {e}")
        raise e
    
    return posts

def collect_instagram_posts(query: str = "politics", max_posts: int = 20) -> List[Dict]:
    posts = []
    
    mock_instagram_posts = [
        {
            "title": f"Amazing {query} tutorial! 🔥",
            "content": f"Check out this awesome {query} content! #coding #programming",
            "author": f"dev_{query.replace(' ', '_')}",
            "url": f"https://www.instagram.com/p/abc123{query.replace(' ', '')}/",
            "score": 1250
        },
        {
            "title": f"Learning {query} step by step 📚",
            "content": f"Day 1 of my {query} journey. So excited to share my progress!",
            "author": f"learner_{query.replace(' ', '_')}",
            "url": f"https://www.instagram.com/p/def456{query.replace(' ', '')}/",
            "score": 890
        },
        {
            "title": f"Best {query} tips and tricks 💡",
            "content": f"Here are my favorite {query} tips that helped me improve!",
            "author": f"tips_{query.replace(' ', '_')}",
            "url": f"https://www.instagram.com/p/ghi789{query.replace(' ', '')}/",
            "score": 2100
        },
        {
            "title": f"{query} project showcase 🚀",
            "content": f"Just finished my latest {query} project! What do you think?",
            "author": f"creator_{query.replace(' ', '_')}",
            "url": f"https://www.instagram.com/p/jkl012{query.replace(' ', '')}/",
            "score": 1560
        },
        {
            "title": f"Behind the scenes: {query} development 🎬",
            "content": f"Working on some cool {query} features. Stay tuned!",
            "author": f"dev_team_{query.replace(' ', '_')}",
            "url": f"https://www.instagram.com/p/mno345{query.replace(' ', '')}/",
            "score": 980
        }
    ]
    
    for i, mock_post in enumerate(mock_instagram_posts[:max_posts]):
        posts.append({
            "source": "Instagram",
            "title": clean_text(mock_post["title"]),
            "content": clean_text(mock_post["content"]),
            "author": mock_post["author"],
            "url": mock_post["url"],
            "score": mock_post["score"],
            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    print(f"Instagram scraping completed: {len(posts)} posts found (mock data)")
    return posts

def collect_instagram_profile_posts(username: str, max_posts: int = 20) -> List[Dict]:
    posts = []
    
    try:
        L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=True,
            save_metadata=True,
            compress_json=False
        )
        
        instagram_username = os.getenv("INSTAGRAM_USERNAME")
        instagram_password = os.getenv("INSTAGRAM_PASSWORD")
        
        if instagram_username and instagram_password:
            try:
                L.login(instagram_username, instagram_password)
                print("✅ Instagram login successful")
            except Exception as e:
                print(f"⚠️ Instagram login failed: {e}")
        
        profile = instaloader.Profile.from_username(L.context, username)
        
        post_count = 0
        for post in profile.get_posts():
            if post_count >= max_posts:
                break
                
            try:
                comments = []
                for comment in post.get_comments():
                    comments.append(comment.text)
                    if len(comments) >= 5:
                        break
                
                likes_count = post.likes if hasattr(post, 'likes') else 0
                
                posts.append({
                    "source": "Instagram",
                    "title": clean_text(post.caption or ""),
                    "content": " | ".join(comments[:3]),
                    "author": post.owner_username,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "score": likes_count,
                    "created_utc": post.date.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                post_count += 1
                
            except Exception as e:
                print(f"Error processing Instagram post: {e}")
                continue
                
    except Exception as e:
        print(f"Instagram profile scraping error: {e}")
    
    return posts
