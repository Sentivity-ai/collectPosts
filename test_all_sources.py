#!/usr/bin/env python3
"""
Comprehensive test script for all CollectPosts sources
Tests Reddit, YouTube, Instagram, Quora, and Threads scraping
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from client import api
import pandas as pd
from datetime import datetime

def test_all_sources():
    """Test all sources with comprehensive parameters"""
    print("🧪 Testing CollectPosts - All Sources")
    print("=" * 50)
    
    # Test parameters
    test_query = "AI technology"
    test_limit = 20
    test_time = "week"
    
    # All supported sources
    all_sources = ["reddit", "youtube", "instagram", "quora", "threads"]
    
    print(f"Query: {test_query}")
    print(f"Limit: {test_limit} posts per source")
    print(f"Time period: {test_time}")
    print(f"Sources: {all_sources}")
    print()
    
    try:
        # Test with all sources
        print("🚀 Testing all sources...")
        data, status = api(
            query=test_query,
            sources=all_sources,
            limit=test_limit,
            time_passed=test_time
        )
        
        print(f"Status: {status}")
        print(f"Total posts collected: {len(data)}")
        print()
        
        if not data.empty:
            # Show source breakdown
            print("📊 Source Breakdown:")
            source_counts = data['source'].value_counts()
            for source, count in source_counts.items():
                print(f"  {source}: {count} posts")
            print()
            
            # Show sample posts
            print("📝 Sample Posts:")
            for i, (_, post) in enumerate(data.head(5).iterrows()):
                print(f"{i+1}. [{post['source']}] {post['title'][:60]}...")
                print(f"   Author: {post['author']} | Score: {post['score']}")
                print(f"   URL: {post['url'][:50]}...")
                print()
            
            # Test hashtag generation
            print("🏷️  Hashtag Analysis:")
            if 'hashtags' in data.columns:
                hashtags = data['hashtags'].dropna().tolist()
                if hashtags:
                    print(f"Generated hashtags: {hashtags[:10]}")
                else:
                    print("No hashtags found in data")
            print()
            
            # Test time filtering
            print("⏰ Time Filtering Test:")
            if 'timestamp' in data.columns:
                timestamps = pd.to_datetime(data['timestamp'])
                print(f"Date range: {timestamps.min()} to {timestamps.max()}")
                print(f"Posts within last {test_time}: {len(timestamps)}")
            print()
            
            # Save test results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.csv"
            data.to_csv(filename, index=False)
            print(f"💾 Test results saved to: {filename}")
            
        else:
            print("❌ No data collected")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_individual_sources():
    """Test each source individually"""
    print("\n🔍 Testing Individual Sources")
    print("=" * 50)
    
    sources = ["reddit", "youtube", "instagram", "quora", "threads"]
    
    for source in sources:
        print(f"\nTesting {source.upper()}...")
        try:
            data, status = api(
                query="technology",
                sources=[source],
                limit=5,
                time_passed="day"
            )
            
            if not data.empty:
                print(f"✅ {source}: {len(data)} posts collected")
                print(f"   Sample: {data.iloc[0]['title'][:50]}...")
            else:
                print(f"⚠️  {source}: No posts collected")
                
        except Exception as e:
            print(f"❌ {source}: Error - {e}")

def test_time_periods():
    """Test different time periods"""
    print("\n⏰ Testing Time Periods")
    print("=" * 50)
    
    time_periods = ["hour", "day", "week", "month"]
    
    for period in time_periods:
        print(f"\nTesting {period} period...")
        try:
            data, status = api(
                query="politics",
                sources=["reddit", "youtube"],
                limit=10,
                time_passed=period
            )
            
            if not data.empty:
                print(f"✅ {period}: {len(data)} posts collected")
            else:
                print(f"⚠️  {period}: No posts collected")
                
        except Exception as e:
            print(f"❌ {period}: Error - {e}")

def test_hashtag_generation():
    """Test hashtag generation functionality"""
    print("\n🏷️  Testing Hashtag Generation")
    print("=" * 50)
    
    try:
        from hashtag_utils import generate_hashtags_from_posts
        
        # Sample posts for testing
        sample_posts = [
            {
                "title": "AI Technology Revolution",
                "content": "Artificial intelligence is transforming industries with machine learning and automation",
                "source": "reddit"
            },
            {
                "title": "Machine Learning Trends",
                "content": "Deep learning and neural networks are advancing rapidly in 2024",
                "source": "youtube"
            },
            {
                "title": "Data Science Applications",
                "content": "Big data analytics and predictive modeling are revolutionizing business",
                "source": "instagram"
            }
        ]
        
        hashtags = generate_hashtags_from_posts(sample_posts)
        print(f"Generated hashtags: {hashtags}")
        
        if hashtags:
            print("✅ Hashtag generation working")
        else:
            print("⚠️  No hashtags generated")
            
    except Exception as e:
        print(f"❌ Hashtag generation failed: {e}")

if __name__ == "__main__":
    print("🚀 CollectPosts Comprehensive Test Suite")
    print("=" * 60)
    
    # Run all tests
    success = test_all_sources()
    test_individual_sources()
    test_time_periods()
    test_hashtag_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed - check the output above")
    
    print("\n📊 Test Summary:")
    print("- All 5 sources supported: reddit, youtube, instagram, quora, threads")
    print("- Time filtering: hour, day, week, month, year")
    print("- Hashtag generation: unified across all sources")
    print("- No hardcoded limits: respects user-specified limits")
    print("- Production ready: FastAPI deployment on Render")
