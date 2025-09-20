from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import os
from datetime import datetime
import uvicorn

from scraper import scrape_posts
from hashtag_utils import (
    generate_hashtags, 
    enhanced_generate_hashtags,
    merge_hashtags_from_sources
)
from upload_utils import upload_dataframe_to_hf
from hive_integration import HiveIntegration, create_hive_ready_csv

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

class ScrapeRequest(BaseModel):
    sources: List[str]
    query: str
    days: int = 7
    limit_per_source: int = 10

class HiveRequest(BaseModel):
    posts: List[dict]
    hive_repo: str
    generate_headlines: bool = True
    upload_to_hf: bool = True

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
async def scrape_multiple_sources(request: ScrapeRequest):
    try:
        # Convert days to time_passed string
        time_mapping = {1: "day", 7: "week", 30: "month", 365: "year"}
        time_passed = time_mapping.get(request.days, "week")
        
        # Use centralized scraping function
        all_posts = scrape_posts(
            sources=request.sources,
            query=request.query,
            time_passed=time_passed,
            limit=request.limit_per_source
        )
        
        # Generate hashtags
        merged_hashtags = enhanced_generate_hashtags(all_posts) if all_posts else []
        
        # Count posts by source
        source_breakdown = {}
        for post in all_posts:
            source = post.get("source", "unknown")
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        return {
            "status": "success",
            "query": request.query,
            "sources": request.sources,
            "days": request.days,
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

@app.get("/test-hf-token")
async def test_hf_token():
    """Test if Hugging Face token is working"""
    try:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            return {
                "status": "error",
                "message": "No HF_TOKEN environment variable set"
            }
        
        from huggingface_hub import HfApi
        api = HfApi()
        
        # Try to get user info to test token
        try:
            user_info = api.whoami(token=hf_token)
            return {
                "status": "success",
                "message": f"HF token is valid. User: {user_info.get('name', 'Unknown')}",
                "user": user_info
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"HF token validation failed: {str(e)}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"HF token test failed: {str(e)}"
        }

@app.post("/hive/process")
async def process_for_hive(request: HiveRequest):
    """Process posts for Hive headline generation workflow"""
    try:
        print(f"Processing {len(request.posts)} posts for Hive...")
        
        # Check if HF token is available
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("Warning: No HF_TOKEN environment variable set")
        
        hive = HiveIntegration()
        
        # Generate Hive-ready CSV
        print("Generating CSV...")
        csv_path = hive.create_headlines_csv(request.posts)
        print(f"CSV generated: {csv_path}")
        
        # Generate summary for headline optimization
        print("Generating summary...")
        summary = hive.generate_headlines_summary(request.posts)
        print(f"Summary generated with {len(summary)} items")
        
        result = {
            "status": "success",
            "csv_path": csv_path,
            "summary": summary,
            "total_posts": len(request.posts)
        }
        
        # Upload to Hugging Face if requested
        if request.upload_to_hf and request.hive_repo:
            print(f"Uploading to HF repo: {request.hive_repo}")
            try:
                upload_result = hive.upload_to_hf_dataset(csv_path, request.hive_repo)
                result["upload_result"] = upload_result
                print(f"Upload result: {upload_result}")
            except Exception as upload_error:
                print(f"Upload error: {str(upload_error)}")
                result["upload_result"] = f"Upload failed: {str(upload_error)}"
        
        # Send to Hive for headline generation if requested
        if request.generate_headlines:
            print("Sending to Hive service...")
            try:
                hive_result = hive.send_to_hive(csv_path)
                result["hive_result"] = hive_result
                print(f"Hive result: {hive_result}")
            except Exception as hive_error:
                print(f"Hive error: {str(hive_error)}")
                result["hive_result"] = f"Hive processing failed: {str(hive_error)}"
        
        print("Hive processing completed successfully")
        return result
        
    except Exception as e:
        print(f"Hive processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Hive processing failed: {str(e)}")

@app.post("/hive/csv")
async def generate_hive_csv(posts: List[dict], filename: Optional[str] = None):
    """Generate Hive-ready CSV file"""
    try:
        csv_path = create_hive_ready_csv(posts)
        return {
            "status": "success",
            "csv_path": csv_path,
            "filename": os.path.basename(csv_path),
            "total_posts": len(posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hive/summary")
async def get_hive_summary(posts: List[dict]):
    """Get summary statistics for headline generation"""
    try:
        hive = HiveIntegration()
        summary = hive.generate_headlines_summary(posts)
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
