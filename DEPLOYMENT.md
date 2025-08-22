# 🚀 Render Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Code pushed to GitHub
- [x] `render.yaml` configured
- [x] `runtime.txt` created
- [x] `Procfile` created
- [x] Web interface updated for production
- [x] Environment variables documented

## 🎯 Deployment Steps

### 1. Create Render Account
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Sign up with GitHub account
3. Verify your email

### 2. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `shravan-del/collectPosts`
3. Render will auto-detect the `render.yaml` configuration
4. Click **"Create Web Service"**

### 3. Configure Environment Variables
In your Render dashboard, go to your service → **Environment** → **Add Environment Variable**:

| Variable | Value | Required |
|----------|-------|----------|
| `REDDIT_CLIENT_ID` | Your Reddit client ID | ✅ |
| `REDDIT_CLIENT_SECRET` | Your Reddit client secret | ✅ |
| `YOUTUBE_API_KEY` | Your YouTube API key | ✅ |
| `HF_TOKEN` | Your Hugging Face token | ✅ |
| `INSTAGRAM_USERNAME` | Your Instagram username | ❌ |
| `INSTAGRAM_PASSWORD` | Your Instagram password | ❌ |

### 4. Deploy
1. Click **"Deploy"**
2. Wait for build to complete (5-10 minutes)
3. Your service will be available at: `https://your-service-name.onrender.com`

## 🔗 Service URLs

Once deployed, your service will have these endpoints:

- **Web Interface:** `https://your-service-name.onrender.com/`
- **API Documentation:** `https://your-service-name.onrender.com/docs`
- **Health Check:** `https://your-service-name.onrender.com/health`
- **API Info:** `https://your-service-name.onrender.com/api`

## 🧪 Testing Your Deployment

### Test the Web Interface
1. Visit your service URL
2. Try scraping from different sources
3. Test hashtag generation
4. Test Hugging Face upload

### Test API Endpoints
```bash
# Health check
curl https://your-service-name.onrender.com/health

# Scrape Reddit
curl "https://your-service-name.onrender.com/scrape?source=reddit&query=python&days=7&limit=5"

# Generate hashtags
curl -X POST "https://your-service-name.onrender.com/hashtags" \
  -H "Content-Type: application/json" \
  -d '{"posts": [{"title": "Test", "content": "Test content"}]}'
```

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` for missing dependencies
   - Verify Python version in `runtime.txt`

2. **Service Won't Start**
   - Check environment variables are set correctly
   - Verify `startCommand` in `render.yaml`

3. **API Errors**
   - Check API keys are valid
   - Verify environment variables are set

4. **CORS Issues**
   - Frontend should auto-detect production vs localhost
   - CORS is configured for all origins in development

### Logs
- Check Render dashboard → your service → **Logs**
- Look for error messages during build or runtime

## 📊 Monitoring

### Health Check
Your service includes a health check endpoint:
```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Performance
- Free tier has limitations on requests per minute
- Consider upgrading for production use
- Monitor usage in Render dashboard

## 🔄 Updates

To update your deployed service:
1. Make changes locally
2. Commit and push to GitHub
3. Render will automatically redeploy

Or manually trigger redeploy:
1. Go to Render dashboard
2. Click **"Manual Deploy"**

## 🎉 Success!

Once deployed, you'll have:
- ✅ A live web service accessible worldwide
- ✅ Beautiful web interface for social media analysis
- ✅ RESTful API for programmatic access
- ✅ Multi-source scraping capabilities
- ✅ Advanced hashtag generation
- ✅ Hugging Face integration

Your Social Media Post Collector & Hashtag Generator is now live! 🚀
