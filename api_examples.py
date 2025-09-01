from api_client import scrape_posts, get_hashtags, process_hive, upload_hf, CollectPostsAPI

RENDER_URL = "https://your-app-name.onrender.com"

def example_basic_usage():
    print("BASIC USAGE EXAMPLES")
    print("=" * 50)
    
    print("1. Scraping posts...")
    result = scrape_posts("politics", limit=50, base_url=RENDER_URL)
    print(f"   Found {len(result.get('all_posts', []))} posts")
    
    print("\n2. Generating hashtags...")
    posts = result.get('all_posts', [])
    hashtags = get_hashtags(posts, max_hashtags=20, base_url=RENDER_URL)
    print(f"   Generated {len(hashtags)} hashtags")
    
    print("\n3. Processing for Hive...")
    hive_result = process_hive(posts, base_url=RENDER_URL)
    print(f"   Hive status: {hive_result.get('status', 'Unknown')}")
    
    return result, hashtags, hive_result

def example_advanced_usage():
    print("\nADVANCED USAGE EXAMPLES")
    print("=" * 50)
    
    api = CollectPostsAPI(RENDER_URL)
    
    print("1. Health check...")
    if api.health_check():
        print("   Service is running")
    else:
        print("   Service is down")
        return
    
    print("\n2. Scraping multiple sources...")
    result = api.scrape("tech", sources=["reddit", "youtube"], limit=100, days=7)
    print(f"   Found {len(result.get('all_posts', []))} posts")
    
    print("\n3. Uploading to Hugging Face...")
    posts = result.get('all_posts', [])
    upload_result = api.upload_to_hf(posts, "your-username/tech-posts")
    print(f"   Upload: {upload_result.get('status', 'Unknown')}")
    
    return result, upload_result

def example_batch_processing():
    print("\nBATCH PROCESSING EXAMPLES")
    print("=" * 50)
    
    queries = ["politics", "technology", "sports", "entertainment"]
    all_results = {}
    
    for query in queries:
        print(f"Processing '{query}'...")
        result = scrape_posts(query, limit=25, base_url=RENDER_URL)
        all_results[query] = result
        print(f"   {query}: {len(result.get('all_posts', []))} posts")
    
    return all_results

def example_environment_variables():
    print("\nENVIRONMENT VARIABLES")
    print("=" * 50)
    
    api = CollectPostsAPI()
    print("API client initialized with environment variables")
    
    if api.health_check():
        print("Service is accessible")
    else:
        print("Service not accessible")

def example_error_handling():
    print("\nERROR HANDLING EXAMPLES")
    print("=" * 50)
    
    print("1. Testing with invalid URL...")
    result = scrape_posts("politics", base_url="https://invalid-url.com")
    if "error" in result:
        print(f"   Error caught: {result['error']}")
    
    print("\n2. Testing with invalid service...")
    result = scrape_posts("politics", base_url="https://httpbin.org/404")
    if "error" in result:
        print(f"   Error caught: {result['error']}")

if __name__ == "__main__":
    print("COLLECTPOSTS API EXAMPLES")
    print("=" * 60)
    
    try:
        basic_result, hashtags, hive_result = example_basic_usage()
        advanced_result, upload_result = example_advanced_usage()
        batch_results = example_batch_processing()
        example_environment_variables()
        example_error_handling()
        
        print("\nAll examples completed!")
        print(f"Total posts collected: {len(basic_result.get('all_posts', []))}")
        print(f"Total hashtags: {len(hashtags)}")
        
    except Exception as e:
        print(f"\nExample failed: {str(e)}")
        print("Make sure to update RENDER_URL with your actual service URL")
