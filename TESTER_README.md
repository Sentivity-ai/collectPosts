# CollectPosts - Tester Instructions

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the test script:**
   ```bash
   python test_scrapers.py
   ```

That's it! The test script will automatically test all functionality.

## What Gets Tested

The test script checks:

1. ✅ **Imports** - All scraper modules can be imported
2. ✅ **Reddit Scraper** - Can collect posts from Reddit
3. ✅ **Hashtag Extraction** - Extracts noun-only hashtags correctly
4. ✅ **Date Filtering** - Date range and time period parsing works
5. ✅ **Random Selection** - Random sampling works (except YouTube hard limit)
6. ✅ **Main Scraper** - Full integration test

## Expected Output

You should see:
```
============================================================
CollectPosts - Comprehensive Test Suite
============================================================

TEST 1: Import Check
✅ Reddit scraper imports: PASS
✅ YouTube scraper imports: PASS
✅ Instagram scraper imports: PASS
✅ Quora scraper imports: PASS
✅ Threads scraper imports: PASS

TEST 2: Reddit Scraper
✅ Reddit scraper: PASS - Collected X posts

TEST 3: Hashtag Extraction (Noun-Only)
✅ Hashtag extraction: PASS - Extracted X noun hashtags

TEST 4: Date Filtering
✅ Date range parsing: PASS
✅ Time period parsing: PASS

TEST 5: Random Selection
✅ Random selection (regular): PASS
✅ Random selection (YouTube hard limit): PASS

TEST 6: Main Scraper Integration
✅ Main scraper: PASS - Output file created

============================================================
TEST SUMMARY
============================================================
Total: 6/6 tests passed
🎉 All tests passed!
```

## Troubleshooting

- **If imports fail**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
- **If Reddit scraper fails**: Check that Reddit API credentials are set (they're hardcoded, so should work)
- **If tests timeout**: This is normal for scraping tests - they may take a while

## Notes

- Tests use small limits (3-5 posts) to be fast
- Some tests may show warnings if no data is found (this is normal)
- The test script creates temporary files that are automatically cleaned up

