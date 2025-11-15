import os
import praw
import re
import nltk
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Set
from collections import Counter
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except:
        pass

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Initialize Reddit with proper error handling
try:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID", "F9rgR81aVwJSjyB0cfqzLQ"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET", "jW9w9dSkntRzjlo2_S_HKRxaiSFgVw"),
        user_agent="CollectPosts/1.0 (by /u/collectposts)"
    )
    # Test the connection
    reddit.user.me()
    print("✅ Reddit API connection successful")
except Exception as e:
    print(f"❌ Reddit API connection failed: {e}")
    reddit = None

def clean_text(text: str) -> str:
    """Clean text by removing newlines and extra whitespace"""
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def preprocess_text(text: str) -> str:
    """Preprocess text for hashtag extraction"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'[^a-z0-9\s.,!?]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def get_top_overlapping_subreddits(base_subreddit: str, top_n: int = 19) -> List[str]:
    """
    Gets 19 relevant overlapping subreddits based on the user provided subreddit for a total of 20
    Uses subredditstats.com API to find overlapping subreddits
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Referer': f'https://subredditstats.com/subreddit-user-overlaps/{base_subreddit}',
        'Accept': 'application/json',
    })
    
    try:
        print(f"🔍 Finding overlapping subreddits for r/{base_subreddit}...")
        
        # Get global subreddit distribution
        global_hist_url = f"https://subredditstats.com/api/globalSubredditsIdHist?v={random.random()}"
        global_response = session.get(global_hist_url, timeout=30)
        global_response.raise_for_status()
        global_hist = global_response.json()
        global_total = sum(global_hist.values())
        global_dist = {k: v / global_total for k, v in global_hist.items()}

        # Get subreddit-specific distribution
        subreddit_hist_url = f"https://subredditstats.com/api/subredditNameToSubredditsHist?subredditName={base_subreddit}&v={random.random()}"
        subreddit_response = session.get(subreddit_hist_url, timeout=30)
        subreddit_response.raise_for_status()
        subreddit_hist = subreddit_response.json()
        subreddit_total = sum(subreddit_hist.values())
        subreddit_dist = {k: v / subreddit_total for k, v in subreddit_hist.items()}

        # Calculate multipliers (overlap scores)
        multipliers = {}
        for sid, prob in subreddit_dist.items():
            if sid in global_dist and global_dist[sid] >= 0.0001:
                multipliers[sid] = prob / global_dist[sid]

        if not multipliers:
            print("⚠️ No overlapping subreddits found")
            return []

        # Get subreddit names from IDs
        subreddit_ids = list(multipliers.keys())
        names_response = session.post(
            "https://subredditstats.com/api/specificSubredditIdsToNames",
            json={"subredditIds": subreddit_ids},
            headers={"Content-Type": "application/json"}
        )
        names_response.raise_for_status()
        subreddit_names = names_response.json()

        # Create overlaps list with scores
        overlaps = []
        for i, (sid, score) in enumerate(multipliers.items()):
            if i < len(subreddit_names):
                overlaps.append((subreddit_names[i], round(score, 3)))

        # Sort by score and return top N
        overlaps.sort(key=lambda x: x[1], reverse=True)
        overlapping_subreddits = [name for name, _ in overlaps[:top_n]]
        
        print(f"✅ Found {len(overlapping_subreddits)} overlapping subreddits")
        return overlapping_subreddits

    except Exception as e:
        print(f"❌ Overlap scrape error: {e}")
        return []

def extract_noun_hashtags(posts: List[Dict], max_hashtags: int = 50) -> List[str]:
    """
    Extract noun hashtags from Reddit posts using NLTK POS tagging
    Only returns actual nouns/words, not random strings
    """
    if not posts:
        return []
    
    print(f"🔍 Extracting noun hashtags from {len(posts)} Reddit posts...")
    
    # Combine all text from posts
    all_text = ""
    for post in posts:
        title = post.get("title", "")
        content = post.get("content", "")
        all_text += f" {title} {content}"
    
    # Tokenize and clean text
    words = word_tokenize(all_text.lower())
    
    # Remove stopwords and non-alphabetic words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
    
    # POS tagging to identify nouns
    pos_tags = pos_tag(filtered_words)
    
    # Extract nouns and proper nouns
    nouns = []
    for word, pos in pos_tags:
        if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Nouns and proper nouns
            nouns.append(word)
    
    # Count frequency and get most common nouns
    noun_counts = Counter(nouns)
    top_nouns = [noun for noun, count in noun_counts.most_common(max_hashtags)]
    
    print(f"✅ Extracted {len(top_nouns)} noun hashtags")
    return top_nouns

def generate_enhanced_hashtags(posts: List[Dict], subreddits: List[str], max_hashtags: int = 50) -> List[str]:
    """
    Enhanced hashtag generation using TF-IDF and subreddit names
    Combines subreddit names with top keywords from posts
    """
    if not posts:
        return []
    
    print(f"🔍 Generating enhanced hashtags from {len(posts)} posts across {len(subreddits)} subreddits...")
    
    # Combine all post titles and content into one text block
    documents = [preprocess_text(p["title"]) + " " + preprocess_text(p["content"]) for p in posts]
    
    # Enhanced stopwords list
    base_stopwords = text.ENGLISH_STOP_WORDS
    custom_stopwords = base_stopwords.union({
        'trump', 'biden', 'like', 'just', 'know', 'think', 'thing', 'things', 'people', 'said', 'also',
        'would', 'could', 'should', 'still', 'even', 'one', 'get', 'going', 'see', 'say', 'make', 'made',
        'want', 'need', 'much', 'many', 'really', 'got', 'look', 'take', 'though', 'well', 'without',
        'every', 'around', 'another', 'others', 'done', 'being', 'next', 'used', 'new', 'time', 'way',
        'good', 'great', 'best', 'better', 'bad', 'worst', 'right', 'wrong', 'true', 'false', 'real',
        'fake', 'news', 'post', 'comment', 'reddit', 'user', 'subreddit', 'thread', 'discussion'
    })
    
    stopword_list = list(custom_stopwords)
    
    # Vectorize with TF-IDF
    vectorizer = TfidfVectorizer(
        stop_words=stopword_list,
        token_pattern=r'\b[a-z]{4,}\b',  # Only words 4+ characters
        max_df=0.6,  # Ignore words that appear in more than 60% of documents
        max_features=100
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.sum(axis=0).A1
        word_scores = list(zip(feature_names, tfidf_scores))
        
        # Get top keywords
        top_keywords = sorted(word_scores, key=lambda x: x[1], reverse=True)[:max_hashtags//2]
        top_tags = [f"#{word}" for word, _ in top_keywords]
        
        # Add subreddit names as hashtags
        base_tags = [f"#{s.lower()}" for s in subreddits if s.isalnum() and len(s) > 2]
        
        # Combine and deduplicate
        hashtags = list(dict.fromkeys(base_tags + top_tags))
        
        print(f"✅ Generated {len(hashtags)} enhanced hashtags")
        return hashtags[:max_hashtags]
        
    except Exception as e:
        print(f"⚠️ TF-IDF hashtag generation failed: {e}, falling back to noun extraction")
        return extract_noun_hashtags(posts, max_hashtags)

def collect_reddit_posts_with_overlapper(
    subreddit_name: str = "politics",
    begin_date: datetime = None,
    end_date: datetime = None,
    limit: int = 1000,
    fetch_multiplier: int = 5
) -> List[Dict]:
    """
    Enhanced Reddit scraper with comprehensive overlapper functionality
    Uses multiple strategies and time filters to get maximum coverage
    """
    
    if not reddit:
        print("❌ Reddit API not available")
        return []

    posts: List[Dict] = []
    seen_urls = set()
    
    # Set default date range if not provided
    if not begin_date:
        begin_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    print(f"🔍 Scraping r/{subreddit_name} with comprehensive overlapper from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Comprehensive overlapper: Multiple strategies × Multiple time filters
        time_filters = ["all", "year", "month", "week", "day"]
        strategies = ["top", "controversial", "rising"]
        
        for time_filter in time_filters:
            if len(posts) >= limit:
                break
                
            for strategy in strategies:
                if len(posts) >= limit:
                    break
                    
                try:
                    print(f"📊 Scraping .{strategy}() with time_filter='{time_filter}'...")
                    
                    # Get method dynamically
                    method = getattr(subreddit, strategy)
                    
                    # Calculate fetch limit based on strategy and time filter
                    if strategy == "top":
                        if time_filter == 'all':
                            fetch_limit = min(5000, limit * fetch_multiplier)
                        elif time_filter == 'year':
                            fetch_limit = min(2000, limit * fetch_multiplier)
                        elif time_filter == 'month':
                            fetch_limit = min(1000, limit * fetch_multiplier)
                        else:
                            fetch_limit = min(500, limit * fetch_multiplier)
                        
                        # Use time_filter for top posts
                        for post in method(limit=fetch_limit, time_filter=time_filter):
                            if len(posts) >= limit:
                                break
                            
                            # Check if post is within date range
                            post_time = datetime.utcfromtimestamp(post.created_utc)
                            if post_time < begin_date or post_time > end_date:
                                continue
                            
                            post_url = f"https://reddit.com{getattr(post, 'permalink', '')}"
                            if post_url in seen_urls:
                                continue
                            seen_urls.add(post_url)

                            posts.append({
                                "source": "reddit",
                                "title": clean_text(getattr(post, "title", "")),
                                "content": clean_text(getattr(post, "selftext", "")),
                                "author": (post.author.name if getattr(post, "author", None) else "[deleted]"),
                                "url": post_url,
                                "score": getattr(post, "score", 0),
                                "timestamp": post_time.isoformat() + "Z",
                                "id": post.id,
                                "strategy": strategy,
                                "time_filter": time_filter
                            })
                    else:
                        # For controversial and rising, use smaller limits
                        fetch_limit = min(200, limit - len(posts))
                        
                        for post in method(limit=fetch_limit):
                            if len(posts) >= limit:
                                break
                            
                            # Check if post is within date range
                            post_time = datetime.utcfromtimestamp(post.created_utc)
                            if post_time < begin_date or post_time > end_date:
                                continue
                            
                            post_url = f"https://reddit.com{getattr(post, 'permalink', '')}"
                            if post_url in seen_urls:
                                continue
                            seen_urls.add(post_url)

                            posts.append({
                                "source": "reddit",
                                "title": clean_text(getattr(post, "title", "")),
                                "content": clean_text(getattr(post, "selftext", "")),
                                "author": (post.author.name if getattr(post, "author", None) else "[deleted]"),
                                "url": post_url,
                                "score": getattr(post, "score", 0),
                                "timestamp": post_time.isoformat() + "Z",
                                "id": post.id,
                                "strategy": strategy,
                                "time_filter": time_filter
                            })
                    
                    strategy_posts = len([p for p in posts if p.get('strategy') == strategy and p.get('time_filter') == time_filter])
                    print(f"✅ {strategy}({time_filter}): {strategy_posts} posts")
                    
                except Exception as e:
                    print(f"⚠️ Error with {strategy}({time_filter}): {e}")
                    continue

    except Exception as e:
        print(f"❌ Reddit scraping error: {e}")

    # Remove strategy and time_filter fields from final output
    for post in posts:
        if 'strategy' in post:
            del post['strategy']
        if 'time_filter' in post:
            del post['time_filter']

    print(f"✅ Reddit comprehensive overlapper completed: {len(posts)} posts found")
    return posts

def scrape_all_sources_via_reddit(
    seed_subreddit: str = "technology", 
    time_period: str = "Past 6 Months", 
    post_limit: int = 1000,
    begin_date: datetime = None,
    end_date: datetime = None
) -> tuple[List[Dict], List[str]]:
    """
    Main function that scrapes all sources via Reddit-driven hashtag architecture
    
    Args:
        seed_subreddit: Base subreddit to start with
        time_period: Time period for scraping ("Past Day", "Past Week", "Past Month", "Past 3 Months", "Past 6 Months", "Past Year")
        post_limit: Maximum total posts to collect across all subreddits
        begin_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
    
    Returns:
        tuple: (all_posts, hashtag_bank)
    """
    print(f"🚀 Starting Reddit-driven hashtag architecture for r/{seed_subreddit}")
    print(f"📅 Time period: {time_period}")
    print(f"🎯 Target: {post_limit} posts across multiple subreddits")
    
    # Step 1: Get overlapping subreddits
    print(f"\n🔍 Step 1: Finding overlapping subreddits...")
    overlapping_subreddits = get_top_overlapping_subreddits(seed_subreddit, top_n=19)
    all_subreddits = [seed_subreddit] + overlapping_subreddits
    print(f"✅ Found {len(all_subreddits)} total subreddits: {all_subreddits[:5]}...")
    
    # Step 2: Set up date filtering
    if not begin_date or not end_date:
        period_map = {
            "Past Day": (1, "day"),
            "Past Week": (7, "week"), 
            "Past Month": (30, "month"),
            "Past 3 Months": (90, "month"),
            "Past 6 Months": (180, "year"),
            "Past Year": (365, "all")
        }
        days, time_filter = period_map.get(time_period, (180, "year"))
        end_date = datetime.utcnow()
        begin_date = end_date - timedelta(days=days)
    
    print(f"📅 Date range: {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Step 3: Scrape all subreddits
    print(f"\n🔍 Step 2: Scraping posts from {len(all_subreddits)} subreddits...")
    all_posts = []
    posts_per_subreddit = max(50, post_limit // len(all_subreddits))  # Distribute posts across subreddits
    
    for i, subreddit in enumerate(all_subreddits):
        if len(all_posts) >= post_limit:
            break
            
        print(f"\n📊 Scraping r/{subreddit} ({i+1}/{len(all_subreddits)})...")
        
        try:
            posts = collect_reddit_posts_with_overlapper(
                subreddit_name=subreddit,
                begin_date=begin_date,
                end_date=end_date,
                limit=posts_per_subreddit,
                fetch_multiplier=3
            )
            
            # Add subreddit origin to each post
            for post in posts:
                post["subreddit_origin"] = subreddit
            
            all_posts.extend(posts)
            print(f"✅ r/{subreddit}: {len(posts)} posts collected")
            
        except Exception as e:
            print(f"❌ Error scraping r/{subreddit}: {e}")
            continue
    
    # Step 4: Generate enhanced hashtags
    print(f"\n🏷️ Step 3: Generating enhanced hashtag bank...")
    print(f"📊 Processing {len(all_posts)} posts from {len(all_subreddits)} subreddits")
    
    hashtag_bank = generate_enhanced_hashtags(all_posts, all_subreddits, max_hashtags=100)
    
    print(f"✅ Generated {len(hashtag_bank)} hashtags")
    print(f"📝 Sample hashtags: {hashtag_bank[:10]}")
    
    # Step 5: Summary
    print(f"\n📊 Final Summary:")
    print(f"✅ Total posts collected: {len(all_posts)}")
    print(f"✅ Subreddits scraped: {len(all_subreddits)}")
    print(f"✅ Hashtags generated: {len(hashtag_bank)}")
    
    # Count posts by subreddit
    subreddit_counts = {}
    for post in all_posts:
        subreddit = post.get("subreddit_origin", "unknown")
        subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
    
    print(f"📈 Posts per subreddit:")
    for subreddit, count in sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   r/{subreddit}: {count} posts")
    
    return all_posts, hashtag_bank

