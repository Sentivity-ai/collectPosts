# Authentication Setup Guide

## Instagram Authentication

Instagram scraping works best with authentication. Here's how to set it up:

### 1. Create a Burner Instagram Account
- Create a new Instagram account specifically for scraping
- Use a real email address (you may need to verify it)
- Complete the account setup

### 2. Set Environment Variables
Add these to your `.env` file or Render environment variables:

```
INSTAGRAM_USERNAME=sentivityburner
INSTAGRAM_PASSWORD=sairam77
```

### 3. How It Works
- The scraper will attempt to login using these credentials
- Sessions are saved to avoid repeated logins
- Authenticated requests have higher rate limits and better access

### 4. Security Notes
- Never commit credentials to git
- Use a burner account (not your personal account)
- The account may get rate-limited if used too aggressively

## Quora Authentication

Quora has strong anti-scraping measures. Options:

### Option 1: Quora API (if available)
- Check if Quora offers an official API
- Requires API key if available

### Option 2: Session-based Scraping
- Manually log into Quora in a browser
- Extract session cookies
- Use cookies in requests (not implemented yet)

### Current Status
- Basic web scraping attempted
- Limited success due to anti-scraping measures
- Authentication would improve results significantly

## Threads Authentication

Threads (Meta) requires authentication similar to Instagram:

### Option 1: Use Instagram Credentials
- Threads uses the same login system as Instagram
- Can potentially use INSTAGRAM_USERNAME/PASSWORD

### Option 2: Threads API (if available)
- Check Meta's Threads API availability
- May require developer access

### Current Status
- Basic web scraping attempted
- Limited success without authentication
- Authentication would improve results significantly

## Testing Authentication

To test if authentication is working:

```python
from instagram_scraper import collect_instagram_posts
from datetime import datetime, timedelta

end = datetime.utcnow()
begin = end - timedelta(days=7)

posts = collect_instagram_posts(
    query="test",
    begin_date=begin,
    end_date=end,
    max_posts=10
)

print(f"Found {len(posts)} posts")
```

If authentication is working, you should see:
- "✅ Instagram login successful"
- More posts returned
- No rate limit warnings

