#!/usr/bin/env python3
"""
API Usage Examples - Simple One-Line Calls
Transform your web service into simple API calls
"""

from api_client import scrape_posts, get_hashtags, process_hive, upload_hf, CollectPostsAPI

# Set your Render service URL
RENDER_URL = "https://your-app-name.onrender.com"  # Replace with your actual URL

def example_basic_usage():
    """Basic one-line usage examples"""
    print("🚀 BASIC USAGE EXAMPLES")
    print("=" * 50)
    
    # 1. Scrape posts in one line
    print("1. Scraping posts...")
    result = scrape_posts("politics", limit=50, base_url=RENDER_URL)
    print(f"   ✅ Found {len(result.get('all_posts', []))} posts")
    
    # 2. Generate hashtags in one line
    print("\n2. Generating hashtags...")
    posts = result.get('all_posts', [])
    hashtags = get_hashtags(posts, max_hashtags=20, base_url=RENDER_URL)
    print(f"   ✅ Generated {len(hashtags)} hashtags")
    
    # 3. Process for Hive in one line
    print("\n3. Processing for Hive...")
    hive_result = process_hive(posts, base_url=RENDER_URL)
    print(f"   ✅ Hive status: {hive_result.get('status', 'Unknown')}")
    
    return result, hashtags, hive_result

def example_advanced_usage():
    """Advanced usage with the API class"""
    print("\n🔧 ADVANCED USAGE EXAMPLES")
    print("=" * 50)
    
    # Initialize API client
    api = CollectPostsAPI(RENDER_URL)
    
    # Check service health
    print("1. Health check...")
    if api.health_check():
        print("   ✅ Service is running")
    else:
        print("   ❌ Service is down")
        return
    
    # Scrape multiple sources
    print("\n2. Scraping multiple sources...")
    result = api.scrape("tech", sources=["reddit", "youtube"], limit=100, days=7)
    print(f"   ✅ Found {len(result.get('all_posts', []))} posts")
    
    # Upload to Hugging Face
    print("\n3. Uploading to Hugging Face...")
    posts = result.get('all_posts', [])
    upload_result = api.upload_to_hf(posts, "your-username/tech-posts")
    print(f"   ✅ Upload: {upload_result.get('status', 'Unknown')}")
    
    return result, upload_result

def example_batch_processing():
    """Batch processing multiple queries"""
    print("\n📊 BATCH PROCESSING EXAMPLES")
    print("=" * 50)
    
    queries = ["politics", "technology", "sports", "entertainment"]
    all_results = {}
    
    for query in queries:
        print(f"Processing '{query}'...")
        result = scrape_posts(query, limit=25, base_url=RENDER_URL)
        all_results[query] = result
        print(f"   ✅ {query}: {len(result.get('all_posts', []))} posts")
    
    return all_results

def example_environment_variables():
    """Using environment variables for configuration"""
    print("\n⚙️  ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    # Set these in your environment or .env file:
    # export COLLECTPOSTS_URL="https://your-app.onrender.com"
    # export HF_TOKEN="your_huggingface_token"
    
    # The API client will automatically use these
    api = CollectPostsAPI()  # No base_url needed
    print("✅ API client initialized with environment variables")
    
    # Test the connection
    if api.health_check():
        print("✅ Service is accessible")
    else:
        print("❌ Service not accessible")

def example_error_handling():
    """Error handling examples"""
    print("\n⚠️  ERROR HANDLING EXAMPLES")
    print("=" * 50)
    
    # Test with invalid URL
    print("1. Testing with invalid URL...")
    result = scrape_posts("politics", base_url="https://invalid-url.com")
    if "error" in result:
        print(f"   ✅ Error caught: {result['error']}")
    
    # Test with invalid service
    print("\n2. Testing with invalid service...")
    result = scrape_posts("politics", base_url="https://httpbin.org/404")
    if "error" in result:
        print(f"   ✅ Error caught: {result['error']}")

if __name__ == "__main__":
    print("🎯 COLLECTPOSTS API EXAMPLES")
    print("=" * 60)
    
    try:
        # Run examples
        basic_result, hashtags, hive_result = example_basic_usage()
        advanced_result, upload_result = example_advanced_usage()
        batch_results = example_batch_processing()
        example_environment_variables()
        example_error_handling()
        
        print("\n🎉 All examples completed!")
        print(f"📊 Total posts collected: {len(basic_result.get('all_posts', []))}")
        print(f"🏷️  Total hashtags: {len(hashtags)}")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        print("💡 Make sure to update RENDER_URL with your actual service URL")
