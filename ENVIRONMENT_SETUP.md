# 🔧 Environment Variables Setup Guide

## Overview

To fix the "undefined" values and 500 errors in your Hive integration, you need to set up the required environment variables on Render.

## 🚨 Current Issues Fixed:

1. **Missing HF_TOKEN**: The Hugging Face token is not set, causing upload failures
2. **Repository Not Found**: The Hugging Face repository doesn't exist (now auto-created)
3. **JSON Serialization Error**: Infinite/NaN values causing JSON errors (now cleaned)
4. **TypeError**: String values in engagement calculation (now converted)

## ✅ Solution: Set Environment Variables on Render

### Step 1: Go to Render Dashboard
1. Visit [https://dashboard.render.com](https://dashboard.render.com)
2. Sign in to your account
3. Find your `social-media-collector` service

### Step 2: Add Environment Variables
1. Click on your service name
2. Go to **Environment** tab
3. Click **Add Environment Variable**
4. Add these variables:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `REDDIT_CLIENT_ID` | `F9rgR81aVwJSjyB0cfqzLQ` | Your Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | `jW9w9dSkntRzjlo2_S_HKRxaiSFgVw` | Your Reddit API client secret |
| `YOUTUBE_API_KEY` | `your_youtube_api_key` | Your YouTube Data API key |
| `HF_TOKEN` | `your_huggingface_token_here` | Your Hugging Face access token |
| `HIVE_SPACE_URL` | `https://huggingface.co/spaces/sentivity/topicfinder` | Your Hive service URL |

### Step 3: Redeploy
1. After adding all environment variables
2. Go to **Manual Deploy** tab
3. Click **Deploy latest commit**
4. Wait for deployment to complete

## 🧪 Testing the Fix

### Test HF Token
```bash
curl https://your-app.onrender.com/test-hf-token
```

Expected response:
```json
{
  "status": "success",
  "message": "HF token is valid. User: your_username",
  "user": {...}
}
```

### Test Hive Processing
1. Go to your app: `https://collectposts.onrender.com`
2. Select sources (Reddit, Quora, Instagram, YouTube)
3. Enter query: "politics"
4. Set limit: 10
5. Enter HF repo: `sentivity/collectPosts`
6. Click **"Process for Hive"** 🐝

Expected result:
- ✅ "Hive Processing Complete" message
- ✅ CSV path displayed
- ✅ Total posts count shown
- ✅ Upload result displayed
- ✅ Headline generation summary

## 🔍 Troubleshooting

### If you still see errors:

1. **Check Environment Variables**:
   ```bash
   curl https://your-app.onrender.com/test-hf-token
   ```

2. **Check Server Logs**:
   - Go to Render dashboard
   - Click on your service
   - Go to **Logs** tab
   - Look for error messages

3. **Common Issues**:
   - **"No HF_TOKEN environment variable set"**: Add the HF_TOKEN variable
   - **"HF token validation failed"**: Check if the token is valid
   - **"Repository Not Found"**: Repository will be auto-created now
   - **"JSON serialization error"**: Data is now cleaned automatically

### Environment Variable Format

**HF_TOKEN**: Must be a valid Hugging Face access token
- Get from: https://huggingface.co/settings/tokens
- Format: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**HIVE_SPACE_URL**: Your Hive service URL
- Format: `https://huggingface.co/spaces/username/service-name`

## 📊 Expected Results After Fix

### Successful Hive Processing:
```json
{
  "status": "success",
  "csv_path": "./outputs/headlines_data_20250831_001234.csv",
  "total_posts": 15,
  "summary": {
    "total_posts": 15,
    "avg_engagement": 456.7,
    "viral_potential": {"high": 3, "medium": 8, "low": 4},
    "recommended_headline_angles": [
      "Focus on politics content (high engagement)",
      "Leverage 3 high-viral-potential posts"
    ]
  },
  "upload_result": "✅ Successfully uploaded headlines_data_20250831_001234.csv to sentivity/collectPosts",
  "hive_result": "✅ Successfully sent to Hive. Generated 5 headlines"
}
```

### Frontend Display:
- ✅ **CSV Generated**: `./outputs/headlines_data_20250831_001234.csv`
- ✅ **Total Posts**: `15`
- ✅ **Upload Result**: Success message
- ✅ **Headline Summary**: Engagement metrics and recommendations

## 🎯 Next Steps

After setting up environment variables:

1. **Test the application**: Use the web interface to process posts
2. **Check CSV generation**: Verify files are created correctly
3. **Monitor uploads**: Ensure data reaches your Hugging Face repository
4. **Integrate with Hive**: Connect your Hive service to process the data

## 📞 Support

If you continue to have issues:

1. **Check Render logs** for detailed error messages
2. **Verify environment variables** are set correctly
3. **Test individual endpoints** using the test URLs above
4. **Contact support** with specific error messages

---

**Once environment variables are set, your Hive integration will work perfectly!** 🚀
