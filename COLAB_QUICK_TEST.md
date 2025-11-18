# Quick Colab Test (Start Here!)

## ⚠️ IMPORTANT: Start Small!

The API can timeout with too many sources/limits. **Start with this simple test first:**

```python
import requests
import pandas as pd
from IPython.display import display

BASE_URL = "https://collectposts.onrender.com"

# STEP 1: Health Check
print("1️⃣ Checking API health...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"✅ API Status: {r.json()}")
except Exception as e:
    print(f"❌ API not responding: {e}")
    print("⚠️  Wait for Render to finish deploying!")

# STEP 2: Simple Test (ONE source, SMALL limit)
print("\n2️⃣ Testing with Reddit only (small limit)...")
try:
    payload = {
        "query": "progun",
        "sources": ["reddit"],  # Only one source!
        "limit_per_source": 20,  # Small limit!
        "days": 7  # One week
    }
    
    r = requests.post(
        f"{BASE_URL}/scrape-multi-source",
        json=payload,
        timeout=120  # 2 minutes
    )
    
    if r.status_code == 200:
        data = r.json()
        posts = data.get("all_posts", [])
        df = pd.DataFrame(posts)
        print(f"✅ Success! Got {len(df)} posts")
        print(f"📊 Breakdown: {data.get('source_breakdown', {})}")
        
        if len(df) > 0:
            display(df.head(5))
    else:
        print(f"❌ Error {r.status_code}: {r.text[:300]}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out. The API might be slow or overloaded.")
    print("💡 Try:")
    print("   - Reducing limit_per_source to 10")
    print("   - Using only ['reddit'] as source")
    print("   - Waiting a few minutes and trying again")
except Exception as e:
    print(f"❌ Error: {e}")

# STEP 3: If Step 2 works, try with YouTube
print("\n3️⃣ If Step 2 worked, try adding YouTube...")
# Uncomment below after Step 2 succeeds:
# payload = {
#     "query": "progun",
#     "sources": ["reddit", "youtube"],  # Two sources
#     "limit_per_source": 30,
#     "days": 7
# }
# r = requests.post(f"{BASE_URL}/scrape-multi-source", json=payload, timeout=180)
# ... (same as Step 2)
```

## Why Timeouts Happen

1. **Too many sources** - Each source takes time to scrape
2. **High limits** - More posts = more processing time
3. **Render free tier** - Can be slow, especially on cold starts
4. **NLTK downloads** - First request might be slower (downloads data)

## Recommended Testing Order

1. ✅ **Health check** - Make sure API is up
2. ✅ **One source, small limit** (reddit, limit=20)
3. ✅ **Two sources, small limit** (reddit + youtube, limit=30)
4. ✅ **Gradually increase** - Add sources/limits one at a time

## If You Still Get Timeouts

1. **Reduce limit_per_source** to 10-20
2. **Use only ['reddit']** as source
3. **Increase timeout** to 300+ seconds
4. **Check Render logs** - Is the API actually processing or stuck?

## Full Test (Only After Simple Tests Work)

Only run the full multi-period test AFTER the simple tests work:

```python
# Only use this after simple tests succeed!
from colab_tester import test_multiple_periods

combined, results = test_multiple_periods(
    query="progun",
    sources=["reddit", "youtube"],  # Start with 2 sources
    limit=30,  # Smaller limit
    periods=["week", "month"]  # Fewer periods
)
```

