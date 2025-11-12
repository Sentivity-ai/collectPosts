#!/usr/bin/env python3
"""
CollectPosts - Social Media Scraper
Main runner script following the exact flow:
1. Scrape Reddit with overlapper
2. Generate hashtag bank (noun-only)
3. Use hashtags to scrape other sources
4. Filter by date range
5. Randomly select posts (except YouTube hard limit)
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reddit_scraper import collect_reddit_posts_with_overlapper, extract_noun_hashtags, scrape_all_sources_via_reddit
from youtube_scraper import collect_youtube_video_titles
from instagram_scraper import collect_instagram_posts
from quora_scraper import scrape_quora
from threads_scraper import scrape_threads

def get_date_range(begin_date_str: str = None, end_date_str: str = None, time_period: str = "week") -> tuple:
    """Get begin and end dates"""
    if begin_date_str and end_date_str:
        return datetime.strptime(begin_date_str, '%Y-%m-%d'), datetime.strptime(end_date_str, '%Y-%m-%d')
    
    time_mapping = {
        "hour": timedelta(hours=1),
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365)
    }
    delta = time_mapping.get(time_period, timedelta(weeks=1))
    end_date = datetime.utcnow()
    begin_date = end_date - delta
    return begin_date, end_date

def filter_posts_by_date(posts: List[Dict], begin_date: datetime, end_date: datetime) -> List[Dict]:
    """Filter posts by date range"""
    filtered = []
    for post in posts:
        try:
            if 'timestamp' in post:
                post_time = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
            elif 'created_utc' in post:
                post_time = datetime.fromisoformat(post['created_utc'].replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                continue
            
            if begin_date <= post_time <= end_date:
                filtered.append(post)
        except:
            continue
    return filtered

def random_sample_posts(posts: List[Dict], limit: int, source: str) -> List[Dict]:
    """Randomly sample posts (except YouTube has hard limit)"""
    if source.lower() == 'youtube':
        return posts[:limit]
    return random.sample(posts, limit) if len(posts) > limit else posts

def main():
    parser = argparse.ArgumentParser(description='CollectPosts - Social Media Scraper')
    parser.add_argument('--subreddit', required=True, help='Subreddit to scrape')
    parser.add_argument('--limit', type=int, default=1000, help='Posts per source (default: 1000)')
    parser.add_argument('--time_period', choices=['hour', 'day', 'week', 'month', 'year'], default='week')
    parser.add_argument('--begin_date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--sources', nargs='+', choices=['reddit', 'youtube', 'instagram', 'quora', 'threads'],
                       default=['reddit', 'youtube', 'instagram', 'quora', 'threads'])
    parser.add_argument('--output', default='scraped_posts.csv')
    parser.add_argument('--youtube_limit', type=int, default=50, help='YouTube hard limit (default: 50)')
    parser.add_argument('--enhanced', action='store_true', help='Use enhanced Reddit overlapper mode')
    parser.add_argument('--post_limit', type=int, default=1000, help='Total posts across subreddits (enhanced mode)')
    parser.add_argument('--time_period_enhanced', default='Past 6 Months',
                       choices=['Past Day', 'Past Week', 'Past Month', 'Past 3 Months', 'Past 6 Months', 'Past Year'])
    
    args = parser.parse_args()
    
    print("🚀 CollectPosts - Social Media Scraper")
    print("=" * 60)
    print(f"Subreddit: r/{args.subreddit}")
    print(f"Sources: {', '.join(args.sources)}")
    print(f"Limit per source: {args.limit}")
    print("=" * 60)
    
    begin_date, end_date = get_date_range(args.begin_date, args.end_date, args.time_period)
    print(f"📅 Date range: {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
    
    all_posts = []
    hashtag_bank = []
    
    if args.enhanced:
        print("🔍 Step 1: Scraping Reddit with enhanced overlapper...")
        all_posts, hashtag_bank = scrape_all_sources_via_reddit(
            seed_subreddit=args.subreddit,
            time_period=args.time_period_enhanced,
            post_limit=args.post_limit,
            begin_date=begin_date,
            end_date=end_date
        )
        print(f"✅ Reddit: {len(all_posts)} posts collected")
        print(f"✅ Hashtag bank: {len(hashtag_bank)} hashtags generated\n")
    else:
        if 'reddit' in args.sources:
            print("🔍 Step 1: Scraping Reddit with overlapper...")
            reddit_posts = collect_reddit_posts_with_overlapper(
                subreddit_name=args.subreddit,
                begin_date=begin_date,
                end_date=end_date,
                limit=args.limit
            )
            reddit_posts = filter_posts_by_date(reddit_posts, begin_date, end_date)
            reddit_posts = random_sample_posts(reddit_posts, args.limit, 'reddit')
            all_posts.extend(reddit_posts)
            print(f"✅ Reddit: {len(reddit_posts)} posts collected")
            
            print("\n🏷️ Step 2: Generating noun-only hashtag bank...")
            hashtag_bank = extract_noun_hashtags(reddit_posts)
            print(f"✅ Hashtag bank: {len(hashtag_bank)} noun hashtags generated\n")
    
    if len(hashtag_bank) > 0 and len(args.sources) > 1:
        print("🔍 Step 3: Scraping other sources using hashtag bank...")
        for source in args.sources:
            if source == 'reddit':
                continue
            
            print(f"\n📱 Scraping {source.upper()}...")
            try:
                if source == 'youtube':
                    posts = collect_youtube_video_titles(
                        query=args.subreddit,
                        hashtags=hashtag_bank,
                        max_results=args.youtube_limit,
                        begin_date=begin_date,
                        end_date=end_date
                    )
                elif source == 'instagram':
                    posts = collect_instagram_posts(
                        query=args.subreddit,
                        hashtags=hashtag_bank,
                        max_posts=args.limit,
                        begin_date=begin_date,
                        end_date=end_date
                    )
                elif source == 'quora':
                    posts = scrape_quora(
                        query=args.subreddit,
                        hashtags=hashtag_bank,
                        time_passed=args.time_period,
                        limit=args.limit,
                        begin_date=begin_date,
                        end_date=end_date
                    )
                elif source == 'threads':
                    posts = scrape_threads(
                        query=args.subreddit,
                        hashtags=hashtag_bank,
                        time_passed=args.time_period,
                        limit=args.limit,
                        begin_date=begin_date,
                        end_date=end_date
                    )
                else:
                    continue
                
                posts = filter_posts_by_date(posts, begin_date, end_date)
                posts = random_sample_posts(posts, args.limit, source)
                all_posts.extend(posts)
                print(f"✅ {source.upper()}: {len(posts)} posts collected")
            except Exception as e:
                print(f"❌ Error scraping {source}: {e}")
                continue
    
    print(f"\n📊 Final Results:")
    print(f"Total posts: {len(all_posts)}")
    
    source_counts = {}
    for post in all_posts:
        source = post.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    if all_posts:
        df = pd.DataFrame(all_posts)
        df.to_csv(args.output, index=False)
        print(f"\n💾 Saved to: {args.output}")
    else:
        print("\n❌ No posts collected")

if __name__ == "__main__":
    main()
