from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
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
    try:
        if source.lower() == "reddit":
            posts = collect_reddit_posts(query, days, limit)
        elif source.lower() == "quora":
            posts = collect_quora_posts(query, limit=limit)
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
        
        merged_hashtags = enhanced_generate_hashtags(all_posts) if all_posts else []
        
        source_breakdown = {}
        for source, result in source_results.items():
            source_breakdown[source] = result.get("posts_count", 0)
        
        return {
            "status": "success",
            "query": query,
            "total_posts": len(all_posts),
            "source_breakdown": source_breakdown,
            "hashtags": merged_hashtags,
            "hashtags_count": len(merged_hashtags),
            "all_posts": all_posts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-source scraping failed: {str(e)}")

@app.post("/upload")
async def upload_to_hf(
    posts: List[Dict] = Body(..., description="List of posts to upload"),
    repo_id: str = Body(..., description="Hugging Face repository ID (e.g., 'username/repo-name')"),
    filename: str = Body("posts.csv", description="Filename for the CSV file")
):
    try:
        if not posts:
            raise HTTPException(status_code=400, detail="No posts provided")
        
        df = pd.DataFrame(posts)
        df["upload_date"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        hashtags = generate_hashtags(posts)
        df["hashtags"] = ", ".join(hashtags)
        
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
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
