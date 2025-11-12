# CollectPosts - Social Media Scraper

A comprehensive social media scraping tool that collects posts from Reddit, YouTube, Instagram, Quora, and Threads using a hashtag-driven architecture.

## How It Works

1. **Reddit Scraping**: Scrapes the specified subreddit using overlapper functionality (finds 19 related subreddits)
2. **Hashtag Bank Generation**: Extracts noun-only hashtags from Reddit posts using NLTK POS tagging
3. **Other Sources**: Uses the hashtag bank to query YouTube, Instagram, Quora, and Threads
4. **Date Filtering**: Filters posts by date range (begin_date/end_date or time_period)
5. **Random Selection**: Randomly samples posts up to limit (except YouTube which has hard limit)

## Features

- ✅ **Reddit Overlapper**: Automatically finds and scrapes 19 related subreddits
- ✅ **Noun-Only Hashtags**: Extracts only actual nouns/words, not random strings
- ✅ **Top Content Only**: All scrapers use `.top()` equivalent methods (not `.new()` or `.hot()`)
- ✅ **Date Filtering**: Optional begin_date/end_date parameters for precise date ranges
- ✅ **Random Selection**: Randomly samples posts (except YouTube hard limit)
- ✅ **Multiple Sources**: Reddit, YouTube, Instagram, Quora, Threads

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main_scraper.py --subreddit technology --limit 1000 --time_period week
```

### With Date Range

```bash
python main_scraper.py --subreddit politics --limit 500 --begin_date 2024-01-01 --end_date 2024-01-31
```

### Enhanced Mode (Reddit Overlapper)

```bash
python main_scraper.py --subreddit technology --enhanced --post_limit 2000 --time_period_enhanced "Past 6 Months"
```

### Specific Sources

```bash
python main_scraper.py --subreddit technology --limit 200 --sources reddit youtube instagram
```

## Arguments

- `--subreddit` (required): Subreddit to scrape
- `--limit`: Posts per source (default: 1000)
- `--time_period`: hour/day/week/month/year (default: week)
- `--begin_date`: Start date (YYYY-MM-DD format)
- `--end_date`: End date (YYYY-MM-DD format)
- `--sources`: Sources to scrape (default: all)
- `--output`: Output CSV file (default: scraped_posts.csv)
- `--youtube_limit`: YouTube hard limit (default: 50)
- `--enhanced`: Use enhanced Reddit overlapper mode
- `--post_limit`: Total posts across subreddits (enhanced mode)
- `--time_period_enhanced`: Time period for enhanced mode

## Configuration

Set environment variables in `.env` file:

```bash
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
OPENAI_API_KEY=your_openai_api_key
```

## Output

Results are saved to CSV with columns:
- `source`: reddit/youtube/instagram/quora/threads
- `title`: Post title/content
- `content`: Full post content
- `author`: Post author
- `url`: Post URL
- `score`: Post score/likes
- `timestamp`: Post timestamp

## Notes

- **YouTube**: Has hard limit of 50 posts to avoid API issues
- **All Scrapers**: Use `.top()` equivalent methods for older time ranges
- **Hashtag Bank**: Only extracts nouns/actual words using NLTK POS tagging
- **Random Selection**: All sources randomly sample except YouTube

## Project Structure

```
collectPosts/
├── main_scraper.py          # Main runner script
├── reddit_scraper.py        # Reddit scraper with overlapper
├── youtube_scraper.py       # YouTube scraper
├── instagram_scraper.py     # Instagram scraper
├── quora_scraper.py         # Quora scraper
├── threads_scraper.py       # Threads scraper
├── analysis.py              # Analysis module (optional)
├── analysis_pipeline.py     # Analysis pipeline (optional)
├── api/                     # API server (optional)
│   └── main.py
├── requirements.txt
└── README.md
```
