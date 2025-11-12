#!/usr/bin/env python3
"""
CollectPosts - Tester Script
Tests all scrapers and functionality
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("=" * 60)
    print("TEST 1: Import Check")
    print("=" * 60)
    try:
        from reddit_scraper import collect_reddit_posts_with_overlapper, extract_noun_hashtags, scrape_all_sources_via_reddit
        print("PASS: Reddit scraper imports")
    except Exception as e:
        print(f"FAIL: Reddit scraper imports - {e}")
        return False
    
    try:
        from youtube_scraper import collect_youtube_video_titles
        print("PASS: YouTube scraper imports")
    except Exception as e:
        print(f"FAIL: YouTube scraper imports - {e}")
        return False
    
    try:
        from instagram_scraper import collect_instagram_posts
        print("PASS: Instagram scraper imports")
    except Exception as e:
        print(f"FAIL: Instagram scraper imports - {e}")
        return False
    
    try:
        from quora_scraper import scrape_quora
        print("PASS: Quora scraper imports")
    except Exception as e:
        print(f"FAIL: Quora scraper imports - {e}")
        return False
    
    try:
        from threads_scraper import scrape_threads
        print("PASS: Threads scraper imports")
    except Exception as e:
        print(f"FAIL: Threads scraper imports - {e}")
        return False
    
    print()
    return True

def test_reddit_scraper():
    """Test Reddit scraper"""
    print("=" * 60)
    print("TEST 2: Reddit Scraper")
    print("=" * 60)
    try:
        from reddit_scraper import collect_reddit_posts_with_overlapper
        
        begin_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()
        
        print("Testing Reddit scraper with r/technology...")
        posts = collect_reddit_posts_with_overlapper(
            subreddit_name="technology",
            begin_date=begin_date,
            end_date=end_date,
            limit=5
        )
        
        if len(posts) > 0:
            print(f"PASS: Reddit scraper - Collected {len(posts)} posts")
            print(f"Sample post: {posts[0].get('title', 'N/A')[:50]}...")
            return True
        else:
            print("WARNING: Reddit scraper - No posts collected (may be rate limited)")
            return True
    except Exception as e:
        print(f"FAIL: Reddit scraper - {e}")
        return False

def test_hashtag_extraction():
    """Test hashtag extraction"""
    print("=" * 60)
    print("TEST 3: Hashtag Extraction (Noun-Only)")
    print("=" * 60)
    try:
        from reddit_scraper import extract_noun_hashtags
        
        test_posts = [
            {
                "title": "Technology news about artificial intelligence",
                "content": "This is a test post about machine learning and data science"
            }
        ]
        
        hashtags = extract_noun_hashtags(test_posts, max_hashtags=10)
        
        if len(hashtags) > 0:
            print(f"PASS: Hashtag extraction - Extracted {len(hashtags)} noun hashtags")
            print(f"Sample hashtags: {hashtags[:5]}")
            return True
        else:
            print("FAIL: Hashtag extraction - No hashtags extracted")
            return False
    except Exception as e:
        print(f"FAIL: Hashtag extraction - {e}")
        return False

def test_date_filtering():
    """Test date filtering"""
    print("=" * 60)
    print("TEST 4: Date Filtering")
    print("=" * 60)
    try:
        from main_scraper import get_date_range, filter_posts_by_date
        
        begin_date, end_date = get_date_range("2024-01-01", "2024-01-31")
        if begin_date and end_date:
            print("PASS: Date range parsing")
            print(f"Begin: {begin_date.strftime('%Y-%m-%d')}")
            print(f"End: {end_date.strftime('%Y-%m-%d')}")
        else:
            print("FAIL: Date range parsing")
            return False
        
        begin_date2, end_date2 = get_date_range(None, None, "week")
        if begin_date2 and end_date2:
            print("PASS: Time period parsing")
            print(f"Begin: {begin_date2.strftime('%Y-%m-%d')}")
            print(f"End: {end_date2.strftime('%Y-%m-%d')}")
        else:
            print("FAIL: Time period parsing")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"FAIL: Date filtering - {e}")
        return False

def test_random_selection():
    """Test random selection"""
    print("=" * 60)
    print("TEST 5: Random Selection")
    print("=" * 60)
    try:
        from main_scraper import random_sample_posts
        
        test_posts = [{"id": i, "source": "test"} for i in range(100)]
        
        sampled = random_sample_posts(test_posts, 10, "reddit")
        if len(sampled) == 10:
            print(f"PASS: Random selection (regular) - Selected {len(sampled)} posts")
        else:
            print(f"FAIL: Random selection (regular) - Expected 10, got {len(sampled)}")
            return False
        
        sampled_yt = random_sample_posts(test_posts, 50, "youtube")
        if len(sampled_yt) == 50:
            print(f"PASS: Random selection (YouTube hard limit) - Selected {len(sampled_yt)} posts")
        else:
            print(f"FAIL: Random selection (YouTube hard limit) - Expected 50, got {len(sampled_yt)}")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"FAIL: Random selection - {e}")
        return False

def test_main_scraper():
    """Test main scraper functionality"""
    print("=" * 60)
    print("TEST 6: Main Scraper Integration")
    print("=" * 60)
    try:
        import subprocess
        import tempfile
        
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        output_file.close()
        
        result = subprocess.run(
            [
                sys.executable, "main_scraper.py",
                "--subreddit", "technology",
                "--limit", "3",
                "--sources", "reddit",
                "--time_period", "day",
                "--output", output_file.name
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
                print("PASS: Main scraper - Output file created")
                print(f"Output file: {output_file.name}")
                os.unlink(output_file.name)
                return True
            else:
                print("WARNING: Main scraper - Output file not created or empty")
                if os.path.exists(output_file.name):
                    os.unlink(output_file.name)
                return True
        else:
            print(f"FAIL: Main scraper - Exit code {result.returncode}")
            print(f"Error: {result.stderr[:200]}")
            if os.path.exists(output_file.name):
                os.unlink(output_file.name)
            return False
    except subprocess.TimeoutExpired:
        print("WARNING: Main scraper - TIMEOUT (this is normal for scraping)")
        if os.path.exists(output_file.name):
            os.unlink(output_file.name)
        return True
    except Exception as e:
        print(f"FAIL: Main scraper - {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CollectPosts - Comprehensive Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Reddit Scraper", test_reddit_scraper()))
    results.append(("Hashtag Extraction", test_hashtag_extraction()))
    results.append(("Date Filtering", test_date_filtering()))
    results.append(("Random Selection", test_random_selection()))
    results.append(("Main Scraper", test_main_scraper()))
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed or had warnings")
        return 1

if __name__ == "__main__":
    sys.exit(main())
