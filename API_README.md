# 🚀 CollectPosts API Client

Transform your deployed CollectPosts web service into **simple one-line API calls**!

## ✨ **What This Gives You**

Instead of making HTTP requests manually, you now have:
- **One-line functions** for all operations
- **Simple CLI commands** for terminal usage
- **Python class** for advanced usage
- **Automatic error handling** and timeouts

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
pip install requests
```

### 2. **Set Your Render Service URL**
```bash
export COLLECTPOSTS_URL="https://your-app-name.onrender.com"
```

### 3. **Use One-Line Functions**
```python
from api_client import scrape_posts, get_hashtags, process_hive

# Scrape posts in one line!
result = scrape_posts("politics", limit=100)

# Generate hashtags in one line!
hashtags = get_hashtags(result['all_posts'], max_hashtags=20)

# Process for Hive in one line!
hive_result = process_hive(result['all_posts'])
```

## 📱 **Usage Examples**

### **Basic One-Line Calls**
```python
from api_client import scrape_posts, get_hashtags, process_hive

# Scrape posts
posts = scrape_posts("technology", sources=["reddit", "youtube"], limit=50)

# Generate hashtags
hashtags = get_hashtags(posts['all_posts'], max_hashtags=15)

# Process for Hive
hive_result = process_hive(posts['all_posts'])
```

### **Advanced Usage with Class**
```python
from api_client import CollectPostsAPI

# Initialize API client
api = CollectPostsAPI("https://your-app.onrender.com")

# Check service health
if api.health_check():
    # Scrape posts
    result = api.scrape("politics", limit=200, days=7)
    
    # Upload to Hugging Face
    upload_result = api.upload_to_hf(result['all_posts'], "username/repo")
```

### **Command Line Interface**
```bash
# Scrape posts
python cli.py scrape "politics" --limit 100 --output results.json

# Generate hashtags
python cli.py hashtags --posts-file results.json --max 20

# Process for Hive
python cli.py hive --posts-file results.json

# Upload to Hugging Face
python cli.py upload --posts-file results.json --repo "username/repo"

# Health check
python cli.py health
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Set your Render service URL
export COLLECTPOSTS_URL="https://your-app-name.onrender.com"

# Set your Hugging Face token (optional)
export HF_TOKEN="your_hf_token_here"
```

### **Direct URL Specification**
```python
# Pass URL directly to functions
result = scrape_posts("politics", base_url="https://your-app.onrender.com")

# Or initialize API client with URL
api = CollectPostsAPI("https://your-app.onrender.com")
```

## 📊 **Available Functions**

### **Core Functions**
- `scrape_posts(query, sources, limit, days)` - Scrape social media posts
- `get_hashtags(posts, max_hashtags)` - Generate hashtags from posts
- `process_hive(posts)` - Process posts for Hive headline generation
- `upload_hf(posts, repo_name)` - Upload posts to Hugging Face

### **API Class Methods**
- `api.scrape()` - Scrape posts with advanced options
- `api.get_hashtags()` - Generate hashtags
- `api.process_for_hive()` - Process for Hive
- `api.upload_to_hf()` - Upload to Hugging Face
- `api.health_check()` - Check service health

### **CLI Commands**
- `scrape` - Scrape posts from command line
- `hashtags` - Generate hashtags from command line
- `hive` - Process for Hive from command line
- `upload` - Upload to Hugging Face from command line
- `health` - Check service health

## 🎯 **Real-World Examples**

### **Batch Processing**
```python
queries = ["politics", "technology", "sports", "entertainment"]
all_results = {}

for query in queries:
    result = scrape_posts(query, limit=25)
    all_results[query] = result
    print(f"{query}: {len(result['all_posts'])} posts")
```

### **Data Pipeline**
```python
# 1. Scrape posts
posts = scrape_posts("AI", limit=100)

# 2. Generate hashtags
hashtags = get_hashtags(posts['all_posts'], max_hashtags=30)

# 3. Process for Hive
hive_result = process_hive(posts['all_posts'])

# 4. Upload to Hugging Face
upload_result = upload_hf(posts['all_posts'], "username/ai-posts")

print(f"Pipeline complete: {len(posts['all_posts'])} posts processed")
```

### **Integration with Other Tools**
```python
import pandas as pd
from api_client import scrape_posts

# Scrape posts
result = scrape_posts("cryptocurrency", limit=200)

# Convert to DataFrame
df = pd.DataFrame(result['all_posts'])

# Save to CSV
df.to_csv('crypto_posts.csv', index=False)

# Analyze data
print(f"Total posts: {len(df)}")
print(f"Sources: {df['source'].value_counts()}")
```

## 🚨 **Error Handling**

The API client automatically handles:
- **Network timeouts** (60s for scraping, 30s for other operations)
- **Service errors** (returns error messages in response)
- **Invalid URLs** (graceful fallback with error messages)
- **Missing files** (clear error messages for CLI operations)

## 🔍 **Troubleshooting**

### **Service Not Responding**
```bash
# Check service health
python cli.py health

# Verify your URL
echo $COLLECTPOSTS_URL
```

### **Authentication Issues**
```bash
# Check Hugging Face token
echo $HF_TOKEN

# Or pass token directly
python cli.py upload --posts-file posts.json --repo "username/repo" --hf-token "your_token"
```

### **Rate Limiting**
- The API client includes automatic timeouts
- Consider implementing delays between batch requests
- Monitor your Render service usage

## 🎉 **You're Ready!**

Now you can transform your web service into simple API calls:

```python
# Before (manual HTTP requests):
# import requests
# response = requests.post("https://your-app.onrender.com/scrape-multi-source", json={...})
# data = response.json()

# After (one-line API calls):
from api_client import scrape_posts
data = scrape_posts("politics", limit=100)  # That's it! 🎯
```

**Happy API-ing!** 🚀
