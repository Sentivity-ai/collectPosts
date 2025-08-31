# Social Media Post Collector & Hashtag Generator

A powerful FastAPI web application that scrapes social media posts from multiple platforms, generates viral hashtags, and integrates with Hive for headline generation.

## 🚀 Features

### 📊 Multi-Platform Scraping
- **Reddit**: Scrape posts from subreddits using PRAW
- **Quora**: Extract questions and answers using BeautifulSoup
- **Instagram**: Collect posts and hashtags using Instaloader
- **YouTube**: Get video titles and descriptions via YouTube Data API

### 🏷️ Advanced Hashtag Generation
- **TF-IDF Analysis**: Extract relevant keywords from post content
- **WordNet Synonyms**: Expand hashtags with semantic variations
- **Trending Detection**: Identify viral and trending topics
- **Frequency Thresholding**: Filter out low-quality hashtags

### 🐝 Hive Integration (NEW!)
- **Headline Generation**: Process posts for viral headline creation
- **Engagement Scoring**: Calculate viral potential and engagement metrics
- **Topic Categorization**: Auto-categorize content (politics, tech, entertainment, etc.)
- **Sentiment Analysis**: Extract viral keywords and sentiment indicators
- **CSV Export**: Generate optimized CSV files for Hive processing
- **Hugging Face Upload**: Direct integration with your Hive service

### 🌐 Modern Web Interface
- **Responsive Design**: Works on desktop and mobile
- **Real-time Analysis**: Instant results with loading indicators
- **Multi-source Selection**: Choose which platforms to analyze
- **Customizable Parameters**: Time range, post limits, and more

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Scraping**: PRAW (Reddit), BeautifulSoup (Quora), Instaloader (Instagram), YouTube API
- **NLP**: scikit-learn (TF-IDF), NLTK (WordNet)
- **Data Processing**: Pandas, NumPy
- **Deployment**: Render, Docker-ready
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/collectPosts.git
cd collectPosts

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
export YOUTUBE_API_KEY="your_youtube_api_key"
export HF_TOKEN="your_huggingface_token"

# Run the application
python main.py
```

### Environment Variables
```bash
# Required for Reddit
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Required for YouTube
YOUTUBE_API_KEY=your_youtube_api_key

# Required for Hive integration
HF_TOKEN=your_huggingface_token

# Optional: Custom Hive service URL
HIVE_SPACE_URL=https://huggingface.co/spaces/sentivity/topicfinder
```

## 🚀 Usage

### Web Interface
1. Open your browser to `http://localhost:8000`
2. Select sources (Reddit, Quora, Instagram, YouTube)
3. Enter your query (subreddit, keyword, or hashtag)
4. Set time range and post limits
5. Click "Analyze" to generate hashtags
6. Click "Process for Hive" 🐝 for headline generation

### API Endpoints

#### Scrape Posts
```bash
# Single source
GET /scrape?source=reddit&query=politics&days=7&limit=10

# Multiple sources
POST /scrape-multi-source
{
  "sources": ["reddit", "quora", "instagram"],
  "query": "politics",
  "days": 7,
  "limit_per_source": 10
}
```

#### Generate Hashtags
```bash
# Basic hashtags
POST /hashtags
{
  "posts": [...]
}

# Enhanced hashtags with synonyms
POST /enhanced-hashtags
{
  "posts": [...]
}
```

#### Hive Integration
```bash
# Generate Hive-ready CSV
POST /hive/csv
{
  "posts": [...]
}

# Get headline generation summary
POST /hive/summary
{
  "posts": [...]
}

# Full Hive processing
POST /hive/process
{
  "posts": [...],
  "hive_repo": "sentivity/collectPosts",
  "generate_headlines": true,
  "upload_to_hf": true
}
```

#### Upload to Hugging Face
```bash
POST /upload
{
  "posts": [...],
  "repo_id": "username/repo-name",
  "filename": "posts.csv"
}
```

## 📊 CSV Output Structure

The Hive integration generates optimized CSV files with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `source` | Platform | "reddit", "quora", "instagram", "youtube" |
| `title` | Post title | "Breaking: Major political scandal revealed" |
| `content` | Post content | "A shocking new report has uncovered..." |
| `author` | Post author | "user123" |
| `score` | Platform score | 1500 |
| `url` | Original URL | "https://reddit.com/r/politics/123" |
| `timestamp` | Post timestamp | "2025-08-22T10:00:00Z" |
| `engagement_score` | Calculated engagement | 700.19 |
| `sentiment_keywords` | Viral keywords | "shocking, breaking, viral" |
| `topic_category` | Auto-categorized | "politics", "technology", "entertainment" |
| `viral_potential` | Viral rating | "high", "medium", "low" |

## 🐝 Hive Integration Features

### Engagement Scoring
- **Weighted Formula**: `(score × 0.4) + (comments × 0.4) + (upvote_ratio × 0.2)`
- **Viral Indicators**: Detects keywords like "breaking", "exclusive", "shocking"
- **Topic Relevance**: Categorizes content for targeted headline generation

### Topic Categories
- **Politics**: election, president, congress, democrat, republican
- **Technology**: tech, AI, software, startup, artificial intelligence
- **Entertainment**: movie, celebrity, music, concert, award
- **Sports**: football, basketball, championship, team
- **Business**: company, stock, market, economy, finance
- **Health**: medical, doctor, hospital, disease, treatment

### Headline Generation Workflow
1. **Data Collection**: Scrape posts from multiple sources
2. **Processing**: Calculate engagement scores and categorize topics
3. **CSV Generation**: Create optimized data structure
4. **Hive Upload**: Send to your Hugging Face Hive service
5. **Headline Creation**: Generate viral headlines based on analysis

## 🚀 Deployment

### Render (Recommended)
1. Fork this repository
2. Connect to Render
3. Set environment variables in Render dashboard
4. Deploy automatically

### Manual Deployment
```bash
# Build and run with Docker
docker build -t social-media-collector .
docker run -p 8000:8000 social-media-collector

# Or deploy to any platform supporting Python
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📁 Project Structure

```
collectPosts/
├── main.py                 # FastAPI application
├── scraper.py             # Social media scraping logic
├── hashtag_utils.py       # Hashtag generation algorithms
├── upload_utils.py        # Hugging Face upload utilities
├── hive_integration.py    # Hive integration for headlines
├── static/
│   └── index.html         # Web interface
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Procfile              # Process file for deployment
├── runtime.txt           # Python version specification
├── test_api.py           # API testing script
├── test_hive.py          # Hive integration tests
├── HIVE_INTEGRATION.md   # Detailed Hive documentation
└── DEPLOYMENT.md         # Deployment guide
```

## 🧪 Testing

### API Testing
```bash
# Test all endpoints
python test_api.py

# Test Hive integration
python test_hive.py
```

### Manual Testing
```bash
# Start the server
python main.py

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/scrape?source=reddit&query=python&days=7&limit=5
```

## 🔧 Configuration

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Get client ID and secret
4. Set environment variables

### YouTube API Setup
1. Go to Google Cloud Console
2. Enable YouTube Data API v3
3. Create API key
4. Set environment variable

### Hugging Face Setup
1. Go to https://huggingface.co/settings/tokens
2. Create access token
3. Set HF_TOKEN environment variable

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: See `HIVE_INTEGRATION.md` for detailed Hive integration guide
- **Deployment**: See `DEPLOYMENT.md` for deployment instructions

## 🎯 Roadmap

- [ ] Real-time streaming updates
- [ ] Advanced sentiment analysis
- [ ] Machine learning-based hashtag optimization
- [ ] Social media scheduling integration
- [ ] Analytics dashboard
- [ ] Multi-language support

---

**Ready to collect posts and generate viral headlines?** 🚀

Your Social Media Post Collector is now fully integrated with Hive for powerful headline generation. Start scraping, analyzing, and creating viral content today!
