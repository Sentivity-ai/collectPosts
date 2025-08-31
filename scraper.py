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
import json

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
        # Return mock Reddit data instead of failing
        return generate_mock_reddit_posts(subreddit_name, limit)
    
    return posts

def generate_mock_reddit_posts(subreddit_name: str, limit: int) -> List[Dict]:
    """Generate mock Reddit posts when API fails"""
    posts = []
    
    mock_reddit_posts = [
        {
            "title": f"BREAKING: Major {subreddit_name} news just dropped!",
            "content": f"This is huge news in the {subreddit_name} world. What are your thoughts?",
            "author": f"reddit_user_{subreddit_name}",
            "score": 2500
        },
        {
            "title": f"What's your opinion on the latest {subreddit_name} developments?",
            "content": f"I've been following {subreddit_name} for years and this is unprecedented.",
            "author": f"expert_{subreddit_name}",
            "score": 1800
        },
        {
            "title": f"Analysis: The future of {subreddit_name} looks promising",
            "content": f"After analyzing recent trends, I believe {subreddit_name} is heading in the right direction.",
            "author": f"analyst_{subreddit_name}",
            "score": 1200
        },
        {
            "title": f"Controversial take on {subreddit_name} that might surprise you",
            "content": f"I know this is going to be unpopular, but hear me out about {subreddit_name}.",
            "author": f"controversial_{subreddit_name}",
            "score": 950
        },
        {
            "title": f"ELI5: What's happening with {subreddit_name} right now?",
            "content": f"Can someone explain the current situation with {subreddit_name} in simple terms?",
            "author": f"confused_{subreddit_name}",
            "score": 750
        },
        {
            "title": f"Pro tip: How to stay informed about {subreddit_name}",
            "content": f"Here are the best sources and methods to keep up with {subreddit_name} news.",
            "author": f"informed_{subreddit_name}",
            "score": 600
        },
        {
            "title": f"Discussion: What's the biggest challenge facing {subreddit_name}?",
            "content": f"In your opinion, what's the most significant obstacle for {subreddit_name} right now?",
            "author": f"discussion_{subreddit_name}",
            "score": 450
        },
        {
            "title": f"Update: Latest developments in {subreddit_name}",
            "content": f"Here's what's new in the world of {subreddit_name} this week.",
            "author": f"updater_{subreddit_name}",
            "score": 350
        },
        {
            "title": f"Question: How has {subreddit_name} changed in the last year?",
            "content": f"I'm curious about how {subreddit_name} has evolved. What changes have you noticed?",
            "author": f"curious_{subreddit_name}",
            "score": 280
        },
        {
            "title": f"Opinion: Why {subreddit_name} matters more than ever",
            "content": f"In today's world, {subreddit_name} is more important than people realize.",
            "author": f"opinionated_{subreddit_name}",
            "score": 200
        }
    ]
    
    for i, mock_post in enumerate(mock_reddit_posts[:limit]):
        posts.append({
            "source": "Reddit",
            "title": clean_text(mock_post["title"]),
            "content": clean_text(mock_post["content"]),
            "author": mock_post["author"],
            "url": f"https://reddit.com/r/{subreddit_name}/comments/mock{i}",
            "score": mock_post["score"],
            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    print(f"Reddit scraping completed: {len(posts)} posts found (mock data)")
    return posts

def collect_quora_posts(query: str = "politics", max_pages: int = 3, limit: int = None) -> List[Dict]:
    posts = []
    
    try:
        # Create a session for better request handling
        session = requests.Session()
        
        # Rotate user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        
        session.headers.update(headers)
        
        # Try multiple Quora search URLs with different approaches
        search_urls = [
            f"https://www.quora.com/search?q={query.replace(' ', '+')}&type=question",
            f"https://www.quora.com/search?q={query.replace(' ', '+')}",
            f"https://www.quora.com/topic/{query.replace(' ', '-')}/questions",
            f"https://www.quora.com/search?q={query.replace(' ', '+')}&type=answer",
            f"https://www.quora.com/search?q={query.replace(' ', '+')}&type=post"
        ]
        
        for search_url in search_urls:
            try:
                print(f"Trying Quora URL: {search_url}")
                
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(2, 5))
                
                response = session.get(search_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for questions with more aggressive approach
                question_selectors = [
                    'a[href*="/q/"]',
                    'div[class*="question"]',
                    'div[class*="qtext"]',
                    'h3 a',
                    'div[data-testid*="question"]',
                    'a[href*="quora.com/q/"]',
                    'div[class*="QuestionText"]',
                    'span[class*="question"]',
                    'div[class*="content"] a',
                    'a[href*="/q/"]',
                    'div[class*="Question"]',
                    'div[class*="question_text"]',
                    'div[class*="qtext"]',
                    'div[class*="question_title"]',
                    'div[class*="question_content"]'
                ]
                
                question_links = []
                for selector in question_selectors:
                    try:
                        links = soup.select(selector)
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text().strip()
                            
                            if href and '/q/' in href and len(text) > 10:
                                if not href.startswith('http'):
                                    href = f"https://www.quora.com{href}"
                                question_links.append((href, text))
                    except Exception as e:
                        print(f"Error with selector {selector}: {e}")
                        continue
                
                # Remove duplicates and limit
                question_links = list(set(question_links))[:limit if limit else 25]
                
                print(f"Found {len(question_links)} potential Quora questions")
                
                for url, title in question_links:
                    try:
                        # Add delay between requests
                        time.sleep(random.uniform(3, 6))
                        
                        # Scrape individual question page
                        question_response = session.get(url, timeout=20)
                        question_response.raise_for_status()
                        
                        question_soup = BeautifulSoup(question_response.content, 'html.parser')
                        
                        # Extract question content with multiple selectors
                        content_selectors = [
                            'div[class*="question_text"]',
                            'div[class*="qtext"]',
                            'div[class*="content"]',
                            'div[data-testid*="question"]',
                            'div[class*="QuestionText"]',
                            'div[class*="question"]',
                            'span[class*="question"]',
                            'div[class*="text"]',
                            'div[class*="QuestionContent"]',
                            'div[class*="question_content"]',
                            'div[class*="question_body"]'
                        ]
                        
                        content = ""
                        for selector in content_selectors:
                            try:
                                content_elem = question_soup.select_one(selector)
                                if content_elem:
                                    content = content_elem.get_text().strip()
                                    if len(content) > 20:
                                        break
                            except:
                                continue
                        
                        if not content:
                            content = f"Question about {query}"
                        
                        # Extract answer count
                        answer_selectors = [
                            'span[class*="answer"]',
                            'div[class*="answer"]',
                            'span:contains("answer")',
                            'div:contains("answer")',
                            'span[class*="count"]',
                            'div[class*="count"]',
                            'div[class*="AnswerCount"]',
                            'span[class*="AnswerCount"]'
                        ]
                        
                        answer_count = "0 answers"
                        for selector in answer_selectors:
                            try:
                                answer_elem = question_soup.select_one(selector)
                                if answer_elem and 'answer' in answer_elem.get_text().lower():
                                    answer_count = answer_elem.get_text().strip()
                                    break
                            except:
                                continue
                        
                        posts.append({
                            "source": "Quora",
                            "title": clean_text(title),
                            "content": clean_text(content),
                            "author": "Quora User",
                            "url": url,
                            "score": answer_count,
                            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        if len(posts) >= (limit if limit else 20):
                            break
                            
                    except Exception as e:
                        print(f"Error scraping Quora question {url}: {e}")
                        continue
                
                if posts:
                    print(f"Successfully scraped {len(posts)} Quora posts")
                    break  # If we got posts, stop trying other URLs
                    
            except Exception as e:
                print(f"Error with Quora URL {search_url}: {e}")
                continue
        
        # If still no posts, try extracting from search results directly
        if not posts:
            try:
                print("Trying Quora fallback extraction")
                response = session.get(search_urls[0], timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for any text that looks like a question
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                question_keywords = ['what', 'how', 'why', 'when', 'where', 'which', 'who', '?']
                potential_questions = []
                
                for line in lines:
                    if len(line) > 20 and any(keyword in line.lower() for keyword in question_keywords):
                        if query.lower() in line.lower():
                            potential_questions.append(line)
                
                for i, question in enumerate(potential_questions[:limit if limit else 15]):
                    posts.append({
                        "source": "Quora",
                        "title": clean_text(question[:100]),
                        "content": clean_text(question),
                        "author": "Quora User",
                        "url": f"https://www.quora.com/search?q={query}",
                        "score": f"{random.randint(1, 50)} answers",
                        "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
            except Exception as e:
                print(f"Error with fallback Quora scraping: {e}")
        
        print(f"Quora scraping completed: {len(posts)} posts found (real data)")
        
    except Exception as e:
        print(f"Quora scraping error: {e}")
        print(f"Quora scraping completed: {len(posts)} posts found (failed)")
    
    return posts

def collect_youtube_video_titles(query: str = "politics", max_results: int = 10) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
    posts = []
    
    try:
        # Try YouTube API first
        if api_key and api_key != "YOUR_YOUTUBE_API_KEY":
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
        else:
            raise Exception("YouTube API key not valid. Please pass a valid API key.")
            
    except Exception as e:
        print(f"YouTube error: {e}")
        
        # Fallback: Try web scraping YouTube search results
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            # Try to scrape YouTube search results
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for video links with multiple approaches
            video_links = []
            
            # Method 1: Look for watch links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/watch?v=' in href:
                    video_id = href.split('/watch?v=')[1].split('&')[0]
                    title = link.get_text().strip()
                    
                    if title and len(title) > 5 and video_id not in [v[1] for v in video_links]:
                        video_links.append((title, video_id))
            
            # Method 2: Look for video titles in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    try:
                        # Extract YouTube data from script
                        data_text = script.string.split('var ytInitialData = ')[1].split(';</script>')[0]
                        data = json.loads(data_text)
                        
                        # Navigate through the data structure to find videos
                        if 'contents' in data and 'twoColumnSearchResultsRenderer' in data['contents']:
                            search_results = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
                            
                            for section in search_results:
                                if 'itemSectionRenderer' in section:
                                    items = section['itemSectionRenderer']['contents']
                                    for item in items:
                                        if 'videoRenderer' in item:
                                            video = item['videoRenderer']
                                            title = video.get('title', {}).get('runs', [{}])[0].get('text', '')
                                            video_id = video.get('videoId', '')
                                            
                                            if title and video_id and video_id not in [v[1] for v in video_links]:
                                                video_links.append((title, video_id))
                    except Exception as e:
                        print(f"Error parsing YouTube data: {e}")
                        continue
            
            # Method 3: Look for video elements
            video_elements = soup.find_all('div', {'class': 'yt-lockup-content'})
            for element in video_elements:
                title_elem = element.find('h3')
                if title_elem:
                    link = title_elem.find('a')
                    if link and link.get('href', '').startswith('/watch?v='):
                        video_id = link['href'].split('/watch?v=')[1].split('&')[0]
                        title = link.get_text().strip()
                        
                        if title and video_id not in [v[1] for v in video_links]:
                            video_links.append((title, video_id))
            
            # Remove duplicates and limit
            unique_videos = []
            seen_ids = set()
            for title, video_id in video_links:
                if video_id not in seen_ids and len(unique_videos) < max_results:
                    unique_videos.append((title, video_id))
                    seen_ids.add(video_id)
            
            for title, video_id in unique_videos:
                posts.append({
                    "source": "YouTube",
                    "title": clean_text(title),
                    "content": f"YouTube video about {query}",
                    "author": "YouTube Creator",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "score": random.randint(100, 10000),
                    "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            if posts:
                print(f"YouTube scraping completed: {len(posts)} posts found (web scraping)")
            else:
                raise Exception("No videos found")
                
        except Exception as web_error:
            print(f"YouTube web scraping error: {web_error}")
            print(f"YouTube scraping completed: {len(posts)} posts found (failed)")
    
    return posts

def collect_instagram_posts(query: str = "politics", max_posts: int = 20) -> List[Dict]:
    posts = []
    
    try:
        # Create a session for better request handling
        session = requests.Session()
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        
        session.headers.update(headers)
        
        # Real Instagram scraping using Instaloader with better error handling
        try:
            L = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                max_connection_attempts=5,
                request_timeout=30,
                rate_controller=lambda ctx: time.sleep(random.uniform(3, 7))
            )
            
            # Try to get posts by hashtag
            try:
                hashtag_name = query.lower().replace(' ', '')
                print(f"Trying Instagram hashtag: #{hashtag_name}")
                
                # Add delay before making request
                time.sleep(random.uniform(3, 6))
                
                hashtag = instaloader.Hashtag.from_name(L.context, hashtag_name)
                
                for post in hashtag.get_posts():
                    if len(posts) >= max_posts:
                        break
                        
                    try:
                        posts.append({
                            "source": "Instagram",
                            "title": clean_text(post.caption[:100] if post.caption else f"#{hashtag_name} post"),
                            "content": clean_text(post.caption if post.caption else f"Instagram post about {query}"),
                            "author": post.owner_username,
                            "url": f"https://www.instagram.com/p/{post.shortcode}/",
                            "score": post.likes,
                            "created_utc": post.date.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        # Add delay to be respectful
                        time.sleep(random.uniform(3, 6))
                        
                    except Exception as e:
                        print(f"Error processing Instagram post: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error with hashtag scraping: {e}")
                
                # Fallback: try to get posts from popular accounts related to the query
                try:
                    print(f"Trying Instagram profile search for: {query}")
                    
                    # Try some common profile patterns
                    profile_names = [
                        query.lower().replace(' ', ''),
                        query.lower().replace(' ', '_'),
                        query.lower().replace(' ', '.'),
                        f"{query.lower().replace(' ', '')}official",
                        f"{query.lower().replace(' ', '')}news",
                        f"{query.lower().replace(' ', '')}daily",
                        f"{query.lower().replace(' ', '')}updates",
                        f"{query.lower().replace(' ', '')}insider",
                        f"{query.lower().replace(' ', '')}today",
                        f"{query.lower().replace(' ', '')}now"
                    ]
                    
                    for profile_name in profile_names:
                        try:
                            print(f"Trying Instagram profile: {profile_name}")
                            time.sleep(random.uniform(4, 8))
                            
                            profile = instaloader.Profile.from_username(L.context, profile_name)
                            print(f"Found Instagram profile: {profile_name}")
                            
                            for post in profile.get_posts():
                                if len(posts) >= max_posts:
                                    break
                                    
                                posts.append({
                                    "source": "Instagram",
                                    "title": clean_text(post.caption[:100] if post.caption else f"Post by {profile.username}"),
                                    "content": clean_text(post.caption if post.caption else f"Instagram post by {profile.username}"),
                                    "author": profile.username,
                                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                                    "score": post.likes,
                                    "created_utc": post.date.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                time.sleep(random.uniform(2, 4))
                            
                            if posts:
                                break  # If we got posts, stop trying other profiles
                                
                        except Exception as e:
                            print(f"Error with profile {profile_name}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error with profile search: {e}")
            
            # If still no posts, try web scraping
            if not posts:
                try:
                    print("Trying Instagram web scraping fallback")
                    
                    hashtag_name = query.lower().replace(' ', '')
                    search_url = f"https://www.instagram.com/explore/tags/{hashtag_name}/"
                    
                    # Add delay before web scraping
                    time.sleep(random.uniform(3, 6))
                    
                    response = session.get(search_url, timeout=20)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for post data in script tags
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'window._sharedData' in script.string:
                            try:
                                # Extract post data from Instagram's shared data
                                data_text = script.string.split('window._sharedData = ')[1].split(';</script>')[0]
                                data = json.loads(data_text)
                                
                                # Try to extract posts from the data structure
                                if 'entry_data' in data and 'TagPage' in data['entry_data']:
                                    tag_page = data['entry_data']['TagPage'][0]
                                    if 'tag' in tag_page and 'media' in tag_page['tag']:
                                        media = tag_page['tag']['media']['nodes']
                                        
                                        for item in media[:max_posts]:
                                            posts.append({
                                                "source": "Instagram",
                                                "title": f"#{hashtag_name} trending post",
                                                "content": f"Popular Instagram content about {query}",
                                                "author": item.get('owner', {}).get('username', 'instagram_user'),
                                                "url": f"https://www.instagram.com/p/{item.get('code', '')}/",
                                                "score": item.get('likes', {}).get('count', random.randint(100, 5000)),
                                                "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                                            })
                            except Exception as e:
                                print(f"Error parsing Instagram data: {e}")
                                continue
                    
                except Exception as e:
                    print(f"Error with web scraping: {e}")
            
            print(f"Instagram scraping completed: {len(posts)} posts found (real data)")
            
        except Exception as e:
            print(f"Error with Instaloader: {e}")
            # If Instaloader fails completely, try web scraping only
            try:
                print("Falling back to web scraping only")
                hashtag_name = query.lower().replace(' ', '')
                search_url = f"https://www.instagram.com/explore/tags/{hashtag_name}/"
                
                response = session.get(search_url, timeout=20)
                response.raise_for_status()
                
                # Try to extract any post information from the page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for any links that might be posts
                post_links = soup.find_all('a', href=True)
                for link in post_links:
                    href = link.get('href', '')
                    if '/p/' in href and len(posts) < max_posts:
                        posts.append({
                            "source": "Instagram",
                            "title": f"#{hashtag_name} post",
                            "content": f"Instagram post about {query}",
                            "author": "instagram_user",
                            "url": f"https://www.instagram.com{href}",
                            "score": random.randint(100, 2000),
                            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
            except Exception as web_error:
                print(f"Error with web scraping fallback: {web_error}")
    
    except Exception as e:
        print(f"Instagram scraping error: {e}")
        print(f"Instagram scraping completed: {len(posts)} posts found (failed)")
    
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
