# 🚀 Social Media Post Collector & Viral Headline Generator

A full-stack Python web application that collects posts from multiple social media platforms, generates viral hashtags, and creates optimized headlines for popular media content.

## ✨ Features

- **Multi-Platform Scraping**: Collect posts from Reddit, Quora, Instagram, and YouTube
- **Intelligent Hashtag Generation**: TF-IDF + WordNet synonym expansion
- **Viral Headline Creation**: AI-powered headline optimization for maximum engagement
- **Hugging Face Integration**: Automatic data upload and storage
- **Hive Service Integration**: Connect to custom headline generation services
- **Modern Web UI**: Clean, responsive interface for easy interaction
- **Robust Error Handling**: Graceful fallbacks and comprehensive error recovery

## 🏗️ Architecture

```
├── main.py              # FastAPI application with REST endpoints
├── scraper.py           # Multi-platform social media scraping
├── hashtag_utils.py     # Advanced hashtag generation algorithms
├── upload_utils.py      # Hugging Face dataset management
├── hive_integration.py  # Headline generation and Hive service integration
├── static/              # Frontend web interface
├── requirements.txt     # Python dependencies
└── render.yaml         # Render deployment configuration
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/collectPosts.git
   cd collectPosts
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export REDDIT_CLIENT_ID="your_reddit_client_id"
   export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
   export YOUTUBE_API_KEY="your_youtube_api_key"
   export HF_TOKEN="your_huggingface_token"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the web interface**
   ```
   http://localhost:8000
   ```

### Production Deployment

The application is configured for deployment on Render. See the [Environment Setup Guide](ENVIRONMENT_SETUP.md) for detailed deployment instructions.

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api` - API information

### Scraping Endpoints

- `GET /scrape?source={platform}&query={keyword}&days={days}&limit={limit}` - Single platform scraping
- `POST /scrape-multi-source` - Multi-platform scraping with JSON body

### Hashtag Generation

- `POST /hashtags` - Basic hashtag generation
- `POST /enhanced-hashtags` - Advanced hashtag generation with synonyms

### Hive Integration

- `POST /hive/process` - Full headline generation workflow
- `POST /hive/csv` - Generate Hive-ready CSV
- `POST /hive/summary` - Generate headline optimization summary
- `GET /test-hf-token` - Test Hugging Face token

### Upload

- `POST /upload` - Upload data to Hugging Face datasets

## 🎯 Usage Examples

### Web Interface

1. **Configure Sources**: Select Reddit, Quora, Instagram, and/or YouTube
2. **Set Parameters**: Enter query, time range, and post limit
3. **Choose Action**:
   - **Analyze**: Generate hashtags and summary
   - **Upload to Hugging Face**: Store data in HF dataset
   - **Process for Hive**: Generate viral headlines

### API Usage

```python
import requests

# Scrape multiple sources
response = requests.post("http://localhost:8000/scrape-multi-source", json={
    "sources": ["reddit", "quora", "instagram"],
    "query": "politics",
    "days": 7,
    "limit_per_source": 10
})

# Process for Hive headlines
hive_response = requests.post("http://localhost:8000/hive/process", json={
    "posts": response.json()["all_posts"],
    "hive_repo": "username/dataset",
    "generate_headlines": True,
    "upload_to_hf": True
})
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | Yes |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | Yes |
| `YOUTUBE_API_KEY` | YouTube Data API key | Yes |
| `HF_TOKEN` | Hugging Face access token | Yes |
| `HIVE_SPACE_URL` | Custom Hive service URL | No |

### Platform-Specific Setup

#### Reddit
1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Get client ID and secret
3. Set environment variables

#### YouTube
1. Enable YouTube Data API v3
2. Create API key at https://console.cloud.google.com
3. Set `YOUTUBE_API_KEY` environment variable

#### Hugging Face
1. Get access token from https://huggingface.co/settings/tokens
2. Set `HF_TOKEN` environment variable

## 🎨 Features in Detail

### Intelligent Hashtag Generation

- **TF-IDF Analysis**: Identifies key terms and phrases
- **WordNet Synonyms**: Expands hashtags with related terms
- **Trending Detection**: Incorporates popular hashtags
- **Topic Relevance**: Filters for context-appropriate tags

### Viral Headline Optimization

- **Engagement Scoring**: Calculates viral potential
- **Topic Categorization**: Politics, Technology, Entertainment, etc.
- **Sentiment Analysis**: Identifies emotional triggers
- **Viral Indicators**: Detects trending keywords

### Robust Error Handling

- **Graceful Fallbacks**: Mock headlines when services unavailable
- **Data Validation**: Handles malformed input gracefully
- **Type Conversion**: Manages string/number conversions
- **JSON Compatibility**: Ensures data serialization

## 🚀 Deployment

### Render Deployment

1. **Connect Repository**: Link your GitHub repo to Render
2. **Configure Environment**: Set all required environment variables
3. **Deploy**: Render will automatically build and deploy
4. **Access**: Your app will be available at `https://your-app.onrender.com`

### Environment Setup

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed deployment instructions.

## 📊 Output Formats

### CSV Structure

Generated CSVs include:
- `source`: Platform (reddit, quora, instagram, youtube)
- `title`: Post title
- `content`: Post content
- `author`: Author username
- `score`: Engagement score
- `url`: Original post URL
- `timestamp`: Post timestamp
- `engagement_score`: Calculated viral potential
- `sentiment_keywords`: Emotional trigger words
- `topic_category`: Content categorization
- `viral_potential`: High/Medium/Low viral rating

### Headline Generation

- **Mock Headlines**: Generated when Hive service unavailable
- **Topic-Specific Formatting**: BREAKING for politics, 🚀 for tech
- **Viral Indicators**: 🔥 VIRAL for high-engagement content
- **Engagement Optimization**: Prioritizes top-performing posts

## 🔍 Troubleshooting

### Common Issues

1. **"No HF_TOKEN environment variable set"**
   - Add your Hugging Face token to environment variables

2. **"Repository Not Found"**
   - Repository will be auto-created if it doesn't exist

3. **"Hive API error: 404"**
   - Mock headlines will be generated automatically

4. **"JSON serialization error"**
   - Data is automatically cleaned for JSON compatibility

### Debug Mode

Enable detailed logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework
- **Hugging Face**: Data storage and model hosting
- **PRAW**: Reddit API wrapper
- **BeautifulSoup**: Web scraping
- **NLTK**: Natural language processing
- **Render**: Deployment platform

---

**Ready to generate viral headlines? Start collecting posts and watch your content go viral!** 🚀
