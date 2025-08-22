#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_scrape_reddit():
    print("\n🔍 Testing Reddit scraping...")
    try:
        response = requests.get(f"{BASE_URL}/scrape", params={
            "source": "reddit",
            "query": "python",
            "days": 7,
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reddit scraping successful: {data['posts_count']} posts collected")
            return True
        else:
            print(f"❌ Reddit scraping failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Reddit scraping error: {e}")
        return False

def test_scrape_quora():
    print("\n🔍 Testing Quora scraping...")
    try:
        response = requests.get(f"{BASE_URL}/scrape", params={
            "source": "quora",
            "query": "python programming",
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quora scraping successful: {data['posts_count']} posts collected")
            return True
        else:
            print(f"❌ Quora scraping failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quora scraping error: {e}")
        return False

def test_scrape_instagram():
    print("\n🔍 Testing Instagram scraping...")
    try:
        response = requests.get(f"{BASE_URL}/scrape", params={
            "source": "instagram",
            "query": "python",
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Instagram scraping successful: {data['posts_count']} posts collected")
            return True
        else:
            print(f"❌ Instagram scraping failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Instagram scraping error: {e}")
        return False

def test_hashtag_generation():
    print("\n🔍 Testing hashtag generation...")
    
    test_posts = [
        {
            "title": "Python Programming Tips",
            "content": "Here are some useful tips for Python programming including best practices and common patterns."
        },
        {
            "title": "Machine Learning with Python",
            "content": "Introduction to machine learning using Python libraries like scikit-learn and TensorFlow."
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/hashtags",
            json=test_posts,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hashtag generation successful: {data['hashtags_count']} hashtags generated")
            print(f"   Sample hashtags: {data['hashtags'][:5]}")
            return True
        else:
            print(f"❌ Hashtag generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Hashtag generation error: {e}")
        return False

def test_enhanced_hashtag_generation():
    print("\n🔍 Testing enhanced hashtag generation...")
    
    test_posts = [
        {
            "title": "Python Programming Tips",
            "content": "Here are some useful tips for Python programming including best practices and common patterns."
        },
        {
            "title": "Machine Learning with Python",
            "content": "Introduction to machine learning using Python libraries like scikit-learn and TensorFlow."
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/enhanced-hashtags",
            json={
                "posts": test_posts,
                "include_synonyms": True,
                "include_trending": True,
                "apply_thresholding": True,
                "topic_keywords": ["python", "programming", "machine learning"],
                "max_hashtags": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced hashtag generation successful: {data['hashtags_count']} hashtags generated")
            print(f"   Features used: {data['features_used']}")
            print(f"   Sample hashtags: {data['hashtags'][:5]}")
            return True
        else:
            print(f"❌ Enhanced hashtag generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enhanced hashtag generation error: {e}")
        return False

def test_multi_source_scraping():
    print("\n🔍 Testing multi-source scraping...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/scrape-multi-source",
            json={
                "sources": ["reddit", "quora"],
                "query": "python",
                "days": 7,
                "limit_per_source": 5
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multi-source scraping successful: {data['total_posts']} total posts")
            print(f"   Sources: {list(data['source_results'].keys())}")
            print(f"   Merged hashtags: {data['hashtags_count']}")
            return True
        else:
            print(f"❌ Multi-source scraping failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Multi-source scraping error: {e}")
        return False

def test_upload_to_hf():
    print("\n🔍 Testing Hugging Face upload...")
    
    if not os.getenv("HF_TOKEN"):
        print("⚠️  Skipping HF upload test - HF_TOKEN not set")
        return True
    
    test_posts = [
        {
            "title": "Test Post 1",
            "content": "This is a test post for API testing.",
            "source": "Test",
            "author": "TestUser",
            "url": "https://example.com",
            "score": 100,
            "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload",
            json={
                "posts": test_posts,
                "repo_id": "test-user/test-repo",
                "filename": f"test_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HF upload successful: {data['message']}")
            return True
        else:
            print(f"❌ HF upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ HF upload error: {e}")
        return False

def main():
    print("🚀 Starting API tests...\n")
    
    tests = [
        test_health,
        test_scrape_reddit,
        test_scrape_quora,
        test_scrape_instagram,
        test_hashtag_generation,
        test_enhanced_hashtag_generation,
        test_multi_source_scraping,
        test_upload_to_hf
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
