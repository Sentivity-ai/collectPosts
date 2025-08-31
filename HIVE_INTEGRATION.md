# 🐝 Hive Integration for Headline Generation

## Overview

The Social Media Post Collector now includes **Hive Integration** - a powerful feature that processes scraped social media posts and generates optimized CSV files for your Hugging Face Hive service to create viral headlines.

## 🎯 What Hive Integration Does

1. **📊 Enhanced Data Processing**: Transforms raw social media posts into structured data optimized for headline generation
2. **🎯 Engagement Scoring**: Calculates viral potential and engagement metrics for each post
3. **📈 Topic Categorization**: Automatically categorizes posts by topic (politics, technology, entertainment, etc.)
4. **🔥 Sentiment Analysis**: Extracts viral keywords and sentiment indicators
5. **📤 Seamless Integration**: Direct upload to your Hugging Face Hive service
6. **📋 Smart Summaries**: Provides headline generation recommendations and insights

## 🚀 How to Use

### 1. Web Interface (Recommended)

1. **Go to your deployed application**: `https://your-app.onrender.com`
2. **Configure your search**:
   - Select sources (Reddit, Quora, Instagram, YouTube)
   - Enter your query (e.g., "politics", "technology", "viral")
   - Set time range and post limits
   - Enter your Hugging Face repository (e.g., `sentivity/collectPosts`)
3. **Click "Process for Hive"** 🐝
4. **View results**: The system will generate a CSV and provide headline insights

### 2. API Endpoints

#### Generate Hive-Ready CSV
```bash
POST /hive/csv
Content-Type: application/json

{
  "posts": [
    {
      "source": "reddit",
      "title": "Breaking news story",
      "content": "Content here...",
      "author": "user123",
      "score": 1500,
      "url": "https://reddit.com/...",
      "timestamp": "2025-08-22T10:00:00Z"
    }
  ]
}
```

#### Get Headline Generation Summary
```bash
POST /hive/summary
Content-Type: application/json

{
  "posts": [...]
}
```

#### Full Hive Processing
```bash
POST /hive/process
Content-Type: application/json

{
  "posts": [...],
  "hive_repo": "sentivity/collectPosts",
  "generate_headlines": true,
  "upload_to_hf": true
}
```

## 📊 CSV Structure

The generated CSV includes these optimized columns:

| Column | Description | Example |
|--------|-------------|---------|
| `source` | Social media platform | "reddit", "quora", "instagram", "youtube" |
| `title` | Post title | "Breaking: Major political scandal revealed" |
| `content` | Post content | "A shocking new report has uncovered..." |
| `author` | Post author | "user123" |
| `score` | Platform score/upvotes | 1500 |
| `url` | Original post URL | "https://reddit.com/r/politics/123" |
| `timestamp` | Post timestamp | "2025-08-22T10:00:00Z" |
| `engagement_score` | Calculated engagement | 700.19 |
| `sentiment_keywords` | Viral/sentiment words | "shocking, breaking, viral" |
| `topic_category` | Auto-categorized topic | "politics", "technology", "entertainment" |
| `viral_potential` | Viral potential rating | "high", "medium", "low" |

## 🎯 Headline Generation Features

### Engagement Scoring
- **Weighted Formula**: `(score × 0.4) + (comments × 0.4) + (upvote_ratio × 0.2)`
- **Viral Indicators**: Detects viral keywords like "breaking", "exclusive", "shocking"
- **Topic Relevance**: Categorizes content for targeted headline generation

### Topic Categories
- **Politics**: election, president, congress, democrat, republican
- **Technology**: tech, AI, software, startup, artificial intelligence
- **Entertainment**: movie, celebrity, music, concert, award
- **Sports**: football, basketball, championship, team
- **Business**: company, stock, market, economy, finance
- **Health**: medical, doctor, hospital, disease, treatment

### Sentiment Analysis
- **Positive**: amazing, incredible, awesome, great, excellent
- **Negative**: terrible, awful, horrible, disgusting, shocking
- **Viral**: viral, trending, breaking, exclusive, controversial

## 🔧 Configuration

### Environment Variables
```bash
# Required for Hugging Face integration
export HF_TOKEN="your_huggingface_token"

# Optional: Custom Hive service URL
export HIVE_SPACE_URL="https://huggingface.co/spaces/sentivity/topicfinder"
```

### Hugging Face Repository
- **Format**: `username/repository-name`
- **Example**: `sentivity/collectPosts`
- **Type**: Dataset repository (recommended)

## 📈 Sample Output

### Headline Generation Summary
```json
{
  "total_posts": 50,
  "sources_breakdown": {
    "reddit": 20,
    "quora": 15,
    "instagram": 10,
    "youtube": 5
  },
  "top_topics": {
    "politics": 15,
    "technology": 12,
    "entertainment": 8
  },
  "viral_potential": {
    "high": 8,
    "medium": 25,
    "low": 17
  },
  "avg_engagement": 456.7,
  "recommended_headline_angles": [
    "Focus on politics content (high engagement)",
    "Leverage 8 high-viral-potential posts",
    "Cover trending topics: politics, technology, entertainment"
  ]
}
```

## 🚀 Workflow Integration

### 1. Data Collection
```python
# Scrape posts from multiple sources
response = requests.post("/scrape-multi-source", json={
    "sources": ["reddit", "quora", "instagram"],
    "query": "politics",
    "days": 7,
    "limit_per_source": 20
})
```

### 2. Hive Processing
```python
# Process for headline generation
response = requests.post("/hive/process", json={
    "posts": response.json()["all_posts"],
    "hive_repo": "sentivity/collectPosts",
    "generate_headlines": True,
    "upload_to_hf": True
})
```

### 3. Headline Generation
- CSV is uploaded to your Hugging Face repository
- Your Hive service processes the data
- Generates viral headlines based on engagement and sentiment analysis

## 🎯 Best Practices

### For Maximum Viral Potential
1. **Target High-Engagement Content**: Focus on posts with engagement scores > 500
2. **Leverage Viral Keywords**: Posts with "breaking", "exclusive", "shocking" perform better
3. **Topic Diversity**: Mix different topics for broader appeal
4. **Timing**: Use recent posts (within 7 days) for current relevance

### CSV Optimization
1. **File Naming**: Use timestamps for version control
2. **Data Quality**: Ensure all required fields are populated
3. **Size Management**: Limit to 100-500 posts per batch for optimal processing

## 🔍 Troubleshooting

### Common Issues

**"No HF_TOKEN environment variable set"**
- Set your Hugging Face token: `export HF_TOKEN="your_token"`

**"CSV file not found"**
- Check that the outputs directory exists
- Verify file permissions

**"Hive API error"**
- Ensure your Hive service is running
- Check the endpoint URL configuration
- Verify authentication tokens

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from hive_integration import HiveIntegration
hive = HiveIntegration()
csv_path = hive.create_headlines_csv(test_posts)
print(f"CSV generated: {csv_path}")
```

## 📚 API Reference

### HiveIntegration Class

```python
class HiveIntegration:
    def __init__(self, hive_space_url=None, hf_token=None)
    def create_headlines_csv(posts, filename=None) -> str
    def generate_headlines_summary(posts) -> dict
    def send_to_hive(csv_path, hive_endpoint=None) -> str
    def upload_to_hf_dataset(csv_path, repo_id, filename=None) -> str
```

### Utility Functions

```python
def create_hive_ready_csv(posts, output_dir="./outputs") -> str
```

## 🎉 Success Metrics

- **CSV Generation**: ✅ Structured data with all required fields
- **Engagement Scoring**: ✅ Accurate viral potential assessment
- **Topic Categorization**: ✅ Automatic content classification
- **Hive Integration**: ✅ Seamless upload to Hugging Face
- **Headline Insights**: ✅ Actionable recommendations for viral content

---

**Ready to generate viral headlines?** 🚀

Your Social Media Post Collector is now fully integrated with Hive for powerful headline generation. The system automatically processes posts, calculates engagement metrics, and provides your Hive service with optimized data for creating viral headlines.
