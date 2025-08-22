from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import pandas as pd
import os
from datetime import datetime
import uvicorn

from scraper import (
    collect_reddit_posts, 
    collect_quora_posts, 
    collect_youtube_video_titles,
    collect_instagram_posts,
    collect_instagram_profile_posts
)
from hashtag_utils import (
    generate_hashtags, 
    enhanced_generate_hashtags,
    merge_hashtags_from_sources
)
from upload_utils import upload_dataframe_to_hf

app = FastAPI(
    title="Social Media Post Collector & Hashtag Generator",
    description="API for collecting posts from Reddit, Quora, and YouTube, generating hashtags, and uploading to Hugging Face",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Social Media Post Collector & Hashtag Generator API",
        "endpoints": {
            "scrape": "/scrape?source=reddit&query=politics&days=30",
            "hashtags": "/hashtags (POST with JSON list of posts)",
            "upload": "/upload (POST with DataFrame and repo ID)"
        }
    }

@app.get("/scrape")
async def scrape_posts(
    source: str = Query(..., description="Source platform: reddit, quora, instagram, instagram_profile, or youtube"),
    query: str = Query(..., description="Search query, subreddit name, hashtag, or Instagram username"),
    days: int = Query(30, description="Number of days to look back (for Reddit)"),
    limit: int = Query(100, description="Maximum number of posts to collect")
):
    """
    Scrape posts from the specified platform
    """
    try:
        if source.lower() == "reddit":
            posts = collect_reddit_posts(query, days, limit)
        elif source.lower() == "quora":
            posts = collect_quora_posts(query, limit=limit)  # Pass limit directly
        elif source.lower() == "instagram":
            posts = collect_instagram_posts(query, limit)
        elif source.lower() == "instagram_profile":
            posts = collect_instagram_profile_posts(query, limit)
        elif source.lower() == "youtube":
            posts = collect_youtube_video_titles(query, limit)
        else:
            raise HTTPException(status_code=400, detail="Invalid source. Use 'reddit', 'quora', 'instagram', 'instagram_profile', or 'youtube'")
        
        return {
            "status": "success",
            "source": source,
            "query": query,
            "posts_count": len(posts),
            "posts": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/hashtags")
async def generate_hashtags_endpoint(posts: List[Dict] = Body(..., description="List of posts with title and content")):
    """
    Generate hashtags from a list of posts
    """
    try:
        if not posts:
            raise HTTPException(status_code=400, detail="No posts provided")
        
        hashtags = generate_hashtags(posts)
        
        return {
            "status": "success",
            "posts_count": len(posts),
            "hashtags_count": len(hashtags),
            "hashtags": hashtags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashtag generation failed: {str(e)}")

@app.post("/enhanced-hashtags")
async def enhanced_hashtags_endpoint(
    posts: List[Dict] = Body(..., description="List of posts with title and content"),
    include_synonyms: bool = Body(True, description="Include WordNet synonyms"),
    include_trending: bool = Body(True, description="Include trending hashtags"),
    apply_thresholding: bool = Body(True, description="Apply frequency thresholding"),
    topic_keywords: List[str] = Body(None, description="Keywords for topic relevance filtering"),
    max_hashtags: int = Body(50, description="Maximum number of hashtags to return")
):
    """
    Generate enhanced hashtags with advanced features
    """
    try:
        if not posts:
            raise HTTPException(status_code=400, detail="No posts provided")
        
        hashtags = enhanced_generate_hashtags(
            posts=posts,
            max_hashtags=max_hashtags,
            include_synonyms=include_synonyms,
            include_trending=include_trending,
            apply_thresholding=apply_thresholding,
            topic_keywords=topic_keywords
        )
        
        return {
            "status": "success",
            "posts_count": len(posts),
            "hashtags_count": len(hashtags),
            "hashtags": hashtags,
            "features_used": {
                "synonyms": include_synonyms,
                "trending": include_trending,
                "thresholding": apply_thresholding,
                "topic_filtering": topic_keywords is not None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced hashtag generation failed: {str(e)}")

@app.post("/scrape-multi-source")
async def scrape_multiple_sources(
    sources: List[str] = Body(..., description="List of sources to scrape: reddit, quora, instagram, youtube"),
    query: str = Body(..., description="Search query for all sources"),
    days: int = Body(30, description="Number of days to look back (for Reddit)"),
    limit_per_source: int = Body(50, description="Maximum posts per source")
):
    """
    Scrape posts from multiple sources simultaneously
    """
    try:
        all_posts = []
        source_results = {}
        
        for source in sources:
            try:
                if source.lower() == "reddit":
                    posts = collect_reddit_posts(query, days, limit_per_source)
                elif source.lower() == "quora":
                    posts = collect_quora_posts(query, limit=limit_per_source)
                elif source.lower() == "instagram":
                    posts = collect_instagram_posts(query, limit_per_source)
                elif source.lower() == "youtube":
                    posts = collect_youtube_video_titles(query, limit_per_source)
                else:
                    continue
                
                source_results[source] = {
                    "posts_count": len(posts),
                    "posts": posts
                }
                all_posts.extend(posts)
                
            except Exception as e:
                source_results[source] = {
                    "error": str(e),
                    "posts_count": 0,
                    "posts": []
                }
        
        # Generate hashtags from all sources combined
        merged_hashtags = enhanced_generate_hashtags(all_posts) if all_posts else []
        
        return {
            "status": "success",
            "query": query,
            "total_posts": len(all_posts),
            "source_results": source_results,
            "merged_hashtags": merged_hashtags,
            "hashtags_count": len(merged_hashtags)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-source scraping failed: {str(e)}")

@app.post("/upload")
async def upload_to_hf(
    posts: List[Dict] = Body(..., description="List of posts to upload"),
    repo_id: str = Body(..., description="Hugging Face repository ID (e.g., 'username/repo-name')"),
    filename: str = Body("posts.csv", description="Filename for the CSV file")
):
    """
    Upload posts to Hugging Face Hub
    """
    try:
        if not posts:
            raise HTTPException(status_code=400, detail="No posts provided")
        
        # Convert posts to DataFrame
        df = pd.DataFrame(posts)
        df["upload_date"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate hashtags and add to DataFrame
        hashtags = generate_hashtags(posts)
        df["hashtags"] = ", ".join(hashtags)
        
        # Upload to Hugging Face
        result = upload_dataframe_to_hf(df, repo_id, filename)
        
        return {
            "status": "success",
            "message": result,
            "posts_count": len(posts),
            "hashtags_count": len(hashtags),
            "filename": filename,
            "repo_id": repo_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
