# Social Media Post Collector & Hashtag Generator

A FastAPI web service that collects posts from Reddit, Quora, and YouTube, generates hashtags using TF-IDF and WordNet, and uploads data to Hugging Face Hub.

## Features

- **Multi-platform scraping**: Reddit (via PRAW), Quora (via BeautifulSoup), YouTube (via API)
- **Intelligent hashtag generation**: Uses TF-IDF and WordNet for relevant hashtags
- **Hugging Face integration**: Upload collected data to HF Hub
- **RESTful API**: Clean endpoints for all operations
- **Easy deployment**: Ready for Render deployment

## API Endpoints

### 1. Scrape Posts
```
GET /scrape?source=reddit&query=politics&days=30&limit=100
```

**Parameters:**
- `source`: Platform to scrape (`reddit`, `quora`, `instagram`, `instagram_profile`, `youtube`)
- `query`: Search query, subreddit name, hashtag, or Instagram username
- `days`: Number of days to look back (Reddit only, default: 30)
- `limit`: Maximum posts to collect (default: 100)

### 2. Enhanced Hashtag Generation
```
POST /enhanced-hashtags
Content-Type: application/json

{
  "posts": [...],
  "include_synonyms": true,
  "include_trending": true,
  "apply_thresholding": true,
  "topic_keywords": ["python", "programming"],
  "max_hashtags": 50
}
```

### 3. Multi-Source Scraping
```
POST /scrape-multi-source
Content-Type: application/json

{
  "sources": ["reddit", "quora", "instagram"],
  "query": "python",
  "days": 30,
  "limit_per_source": 50
}
```

### 4. Generate Hashtags
```
POST /hashtags
Content-Type: application/json

{
  "posts": [
    {
      "title": "Post title",
      "content": "Post content"
    }
  ]
}
```

### 5. Upload to Hugging Face
```
POST /upload
Content-Type: application/json

{
  "posts": [...],
  "repo_id": "username/repo-name",
  "filename": "posts.csv"
}
```

### 6. Health Check
```
GET /health
```

## Local Development

### Prerequisites

- Python 3.8+
- API keys for Reddit, YouTube, and Hugging Face

### Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd collectPosts
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export REDDIT_CLIENT_ID="your_reddit_client_id"
   export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
   export YOUTUBE_API_KEY="your_youtube_api_key"
   export INSTAGRAM_USERNAME="your_instagram_username"  # Optional
   export INSTAGRAM_PASSWORD="your_instagram_password"  # Optional
   export HF_TOKEN="your_huggingface_token"
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API:**
   - API documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Deployment on Render

### Automatic Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python

4. **Set environment variables in Render dashboard:**
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `YOUTUBE_API_KEY`
   - `HF_TOKEN`

### Manual Deployment

1. **Push your code to GitHub**
2. **Use the provided `render.yaml`:**
   ```bash
   # Render will automatically detect and use render.yaml
   ```

## API Usage Examples

### Scrape Reddit Posts
```bash
curl "http://localhost:8000/scrape?source=reddit&query=politics&days=7&limit=50"
```

### Scrape Quora Posts
```bash
curl "http://localhost:8000/scrape?source=quora&query=python%20programming&limit=20"
```

### Scrape Instagram Posts
```bash
curl "http://localhost:8000/scrape?source=instagram&query=python&limit=20"
```

### Generate Enhanced Hashtags
```bash
curl -X POST "http://localhost:8000/enhanced-hashtags" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [
      {
        "title": "Python Programming Tips",
        "content": "Here are some useful tips for Python programming."
      }
    ],
    "include_synonyms": true,
    "include_trending": true,
    "apply_thresholding": true,
    "topic_keywords": ["python", "programming"],
    "max_hashtags": 30
  }'
```

### Multi-Source Scraping
```bash
curl -X POST "http://localhost:8000/scrape-multi-source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["reddit", "quora", "instagram"],
    "query": "python",
    "days": 30,
    "limit_per_source": 50
  }'
```

### Generate Basic Hashtags
```bash
curl -X POST "http://localhost:8000/hashtags" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [
      {
        "title": "Breaking news about politics",
        "content": "This is a detailed article about current political events."
      }
    ]
  }'
```

### Upload to Hugging Face
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [...],
    "repo_id": "your-username/your-repo",
    "filename": "politics_posts.csv"
  }'
```

## Project Structure

```
collectPosts/
├── main.py              # FastAPI application and routes
├── scraper.py           # Scraping logic for Reddit, Quora, YouTube
├── hashtag_utils.py     # TF-IDF and WordNet hashtag generation
├── upload_utils.py      # Hugging Face upload functionality
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment configuration
└── README.md           # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | Yes |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | Yes |
| `YOUTUBE_API_KEY` | YouTube Data API key | Yes |
| `INSTAGRAM_USERNAME` | Instagram username | Optional (for better scraping) |
| `INSTAGRAM_PASSWORD` | Instagram password | Optional (for better scraping) |
| `HF_TOKEN` | Hugging Face access token | For uploads |

## Getting API Keys

### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Copy the client ID and secret

### YouTube API
1. Go to https://console.cloud.google.com/
2. Create a project and enable YouTube Data API v3
3. Create credentials (API key)

### Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with write permissions

## Error Handling

The API includes comprehensive error handling:
- Invalid source platforms return 400 errors
- Missing API keys return appropriate error messages
- Network timeouts and API failures are handled gracefully
- All endpoints return structured JSON responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
