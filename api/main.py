from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime, timedelta
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reddit_scraper import collect_reddit_posts_with_overlapper, extract_noun_hashtags
from youtube_scraper import collect_youtube_video_titles
from instagram_scraper import collect_instagram_posts
from quora_scraper import scrape_quora
from threads_scraper import scrape_threads
import pandas as pd
from analysis_pipeline import cluster_and_summarize, analyze_before_after

app = FastAPI(
    title="CollectPosts API",
    description="Social media scraping API for Reddit, YouTube, and Instagram",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Download NLTK data on startup - ensure it's available before serving requests"""
    import nltk
    import os
    
    # Set NLTK data directory to a writable location
    nltk_data_dir = os.getenv('NLTK_DATA', '/opt/render/nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)
    
    try:
        # Download required NLTK data - punkt_tab is critical for newer NLTK
        print("📥 Downloading NLTK data on startup...")
        
        # Download punkt_tab first (required by newer NLTK)
        try:
            nltk.data.find('tokenizers/punkt_tab')
            print("✅ punkt_tab already available")
        except LookupError:
            print("📥 Downloading punkt_tab...")
            nltk.download('punkt_tab', quiet=True)
        
        # Download punkt for compatibility
        try:
            nltk.data.find('tokenizers/punkt')
            print("✅ punkt already available")
        except LookupError:
            print("📥 Downloading punkt...")
            nltk.download('punkt', quiet=True)
        
        # Download tagger (try both old and new names)
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
            print("✅ averaged_perceptron_tagger already available")
        except LookupError:
            print("📥 Downloading averaged_perceptron_tagger...")
            nltk.download('averaged_perceptron_tagger', quiet=True)
        
        # Download new tagger name (for newer NLTK versions)
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger_eng')
            print("✅ averaged_perceptron_tagger_eng already available")
        except LookupError:
            print("📥 Downloading averaged_perceptron_tagger_eng...")
            nltk.download('averaged_perceptron_tagger_eng', quiet=True)
        
        # Download stopwords
        try:
            nltk.data.find('corpora/stopwords')
            print("✅ stopwords already available")
        except LookupError:
            print("📥 Downloading stopwords...")
            nltk.download('stopwords', quiet=True)
        
        # Download all NLTK data as a fallback (ensures everything is available)
        print("📥 Ensuring all NLTK data is available...")
        try:
            nltk.download('all', quiet=True)
            print("✅ All NLTK data downloaded")
        except Exception as e:
            print(f"⚠️  Could not download all NLTK data: {e}")
        
        print("✅ All NLTK data ready")
    except Exception as e:
        print(f"⚠️  NLTK download warning: {e}")
        import traceback
        traceback.print_exc()

class ScrapeRequest(BaseModel):
    sources: List[str]
    query: str
    days: int = 7
    limit_per_source: int = 10
    begin_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None    # YYYY-MM-DD format

class AnalyzeRequest(BaseModel):
    query: str
    sources: List[str]
    limit_per_source: int = 100
    begin_date: Optional[str] = None
    end_date: Optional[str] = None
    days: int = 7
    min_cluster_size: int = 5
    word_bank: Optional[List[str]] = None
    pop_culture: bool = True
    no_pop_filter: bool = False

class BeforeAfterRequest(BaseModel):
    query: str
    sources: List[str]
    word_bank: List[str]
    before_start: str  # YYYY-MM-DD
    before_end: str    # YYYY-MM-DD
    after_start: str   # YYYY-MM-DD
    after_end: str     # YYYY-MM-DD
    limit_per_source: int = 100
    days: int = 7

@app.get("/")
async def root():
    return {
        "message": "CollectPosts API - Social Media Scraping Service",
        "status": "running",
        "endpoints": {
            "scrape": "/scrape-multi-source (POST)",
            "analyze": "/analyze (POST)",
            "before-after": "/analyze-before-after (POST)",
            "health": "/health (GET)"
        },
        "supported_sources": ["reddit", "youtube", "instagram", "quora", "threads"],
        "time_periods": ["hour", "day", "week", "month", "year"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - responds immediately for port scanning"""
    return {"status": "healthy", "service": "collectposts"}

@app.post("/scrape-multi-source")
async def scrape_multiple_sources(request: ScrapeRequest):
    try:
        # Aggressive limits to prevent timeouts on free tier
        # Reduce limits based on number of sources
        num_sources = len(request.sources)
        if num_sources >= 4:
            max_limit = min(request.limit_per_source, 20)  # Very small for many sources
        elif num_sources >= 3:
            max_limit = min(request.limit_per_source, 30)
        elif num_sources >= 2:
            max_limit = min(request.limit_per_source, 50)
        else:
            max_limit = min(request.limit_per_source, 100)
        
        # Parse date range
        if request.begin_date and request.end_date:
            begin_date = datetime.strptime(request.begin_date, '%Y-%m-%d')
            end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        else:
            # Use time_period
            time_mapping = {1: timedelta(days=1), 7: timedelta(weeks=1), 30: timedelta(days=30), 365: timedelta(days=365)}
            delta = time_mapping.get(request.days, timedelta(weeks=1))
            end_date = datetime.utcnow()
            begin_date = end_date - delta
        
        all_posts = []
        hashtag_bank = set()
        
        # Step 1: Scrape Reddit with overlapper functionality
        if 'reddit' in request.sources:
            try:
                reddit_posts = collect_reddit_posts_with_overlapper(
                    subreddit_name=request.query,
                    begin_date=begin_date,
                    end_date=end_date,
                    limit=max_limit
                )
                all_posts.extend(reddit_posts)
                
                # Extract hashtag bank from Reddit posts (only if we have posts)
                if reddit_posts:
                    hashtag_bank = extract_noun_hashtags(reddit_posts)
            except Exception as e:
                print(f"⚠️  Reddit scraping error: {e}")
                import traceback
                traceback.print_exc()
                # Continue with other sources even if Reddit fails
        
        # Step 2: Use hashtags to scrape other sources
        # If no hashtags from Reddit, use query directly
        search_terms = hashtag_bank if len(hashtag_bank) > 0 else {request.query}
        
        for source in request.sources:
            if source == 'reddit':
                continue  # Already done
                
            try:
                if source == 'youtube':
                    # YouTube gets hard limit
                    posts = collect_youtube_video_titles(
                        query=request.query,
                        hashtags=search_terms,
                        max_results=min(30, max_limit),  # Reduced hard limit
                        begin_date=begin_date,
                        end_date=end_date
                    )
                    
                elif source == 'instagram':
                    posts = collect_instagram_posts(
                        query=request.query,
                        hashtags=search_terms,
                        max_posts=min(20, max_limit),  # Reduced limit
                        begin_date=begin_date,
                        end_date=end_date
                    )
                    
                elif source == 'quora':
                    posts = scrape_quora(
                        query=request.query,
                        hashtags=search_terms,
                        time_passed="week",
                        limit=min(20, max_limit),  # Reduced limit
                        begin_date=begin_date,
                        end_date=end_date
                    )
                    
                elif source == 'threads':
                    posts = scrape_threads(
                        query=request.query,
                        hashtags=search_terms,
                        time_passed="week",
                        limit=min(20, max_limit),  # Reduced limit
                        begin_date=begin_date,
                        end_date=end_date
                    )
                
                # Random sample (except YouTube has hard limit)
                if source != 'youtube' and len(posts) > max_limit:
                    posts = random.sample(posts, max_limit)
                
                all_posts.extend(posts)
                
            except Exception as e:
                print(f"Error scraping {source}: {e}")
                continue
        
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
            "hashtags": list(hashtag_bank),
            "all_posts": all_posts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-source scraping failed: {str(e)}")


@app.post("/analyze")
async def analyze_posts(request: AnalyzeRequest):
    """Analyze and cluster posts with summarization"""
    try:
        # Limit maximum posts to prevent timeouts
        max_limit = min(request.limit_per_source, 500)
        
        # Parse date range
        if request.begin_date and request.end_date:
            begin_date = datetime.strptime(request.begin_date, '%Y-%m-%d')
            end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        else:
            time_mapping = {1: timedelta(days=1), 7: timedelta(weeks=1), 30: timedelta(days=30), 365: timedelta(days=365)}
            delta = time_mapping.get(request.days, timedelta(weeks=1))
            end_date = datetime.utcnow()
            begin_date = end_date - delta
        
        all_posts = []
        hashtag_bank = set()
        
        # Scrape Reddit with overlapper
        if 'reddit' in request.sources:
            reddit_posts = collect_reddit_posts_with_overlapper(
                subreddit_name=request.query,
                begin_date=begin_date,
                end_date=end_date,
                limit=max_limit
            )
            all_posts.extend(reddit_posts)
            hashtag_bank = extract_noun_hashtags(reddit_posts)
        
        # Scrape other sources
        if len(hashtag_bank) > 0:
            for source in request.sources:
                if source == 'reddit':
                    continue
                    
                try:
                    if source == 'youtube':
                        posts = collect_youtube_video_titles(
                            query=request.query,
                            hashtags=hashtag_bank,
                            max_results=min(50, max_limit),
                            begin_date=begin_date,
                            end_date=end_date
                        )
                    elif source == 'instagram':
                        posts = collect_instagram_posts(
                            query=request.query,
                            hashtags=hashtag_bank,
                            max_posts=max_limit,
                            begin_date=begin_date,
                            end_date=end_date
                        )
                    elif source == 'quora':
                        posts = scrape_quora(
                            query=request.query,
                            hashtags=hashtag_bank,
                            time_passed="week",
                            limit=max_limit,
                            begin_date=begin_date,
                            end_date=end_date
                        )
                    elif source == 'threads':
                        posts = scrape_threads(
                            query=request.query,
                            hashtags=hashtag_bank,
                            time_passed="week",
                            limit=max_limit,
                            begin_date=begin_date,
                            end_date=end_date
                        )
                    else:
                        continue
                    
                    if source != 'youtube' and len(posts) > max_limit:
                        posts = random.sample(posts, max_limit)
                    
                    all_posts.extend(posts)
                    
                except Exception as e:
                    print(f"Error scraping {source}: {e}")
                    continue
        
        # Convert to DataFrame
        if not all_posts:
            return {
                "status": "error",
                "message": "No posts found"
            }
        
        df = pd.DataFrame(all_posts)
        
        # Run analysis
        summary_text, clusters = cluster_and_summarize(
            posts_df=df,
            base_subreddit=request.query,
            min_cluster_size=request.min_cluster_size,
            word_bank=request.word_bank,
            pop_culture=request.pop_culture,
            no_pop_filter=request.no_pop_filter
        )
        
        return {
            "status": "success",
            "query": request.query,
            "total_posts": len(all_posts),
            "summary": summary_text,
            "clusters": {str(k): len(v) for k, v in clusters.items()},
            "hashtags": list(hashtag_bank)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze-before-after")
async def analyze_before_after_endpoint(request: BeforeAfterRequest):
    """Analyze posts before and after a launch date"""
    try:
        # Scrape posts for both periods
        all_posts = []
        hashtag_bank = set()
        
        # Scrape Reddit
        if 'reddit' in request.sources:
            # Before period
            before_begin = datetime.strptime(request.before_start, '%Y-%m-%d')
            before_end = datetime.strptime(request.before_end, '%Y-%m-%d')
            reddit_posts_before = collect_reddit_posts_with_overlapper(
                subreddit_name=request.query,
                begin_date=before_begin,
                end_date=before_end,
                limit=request.limit_per_source
            )
            all_posts.extend(reddit_posts_before)
            
            # After period
            after_begin = datetime.strptime(request.after_start, '%Y-%m-%d')
            after_end = datetime.strptime(request.after_end, '%Y-%m-%d')
            reddit_posts_after = collect_reddit_posts_with_overlapper(
                subreddit_name=request.query,
                begin_date=after_begin,
                end_date=after_end,
                limit=request.limit_per_source
            )
            all_posts.extend(reddit_posts_after)
            
            hashtag_bank = extract_noun_hashtags(all_posts)
        
        # Scrape other sources if needed
        # (Similar logic as above)
        
        if not all_posts:
            return {
                "status": "error",
                "message": "No posts found"
            }
        
        df = pd.DataFrame(all_posts)
        
        # Run before/after analysis
        results = analyze_before_after(
            data=df,
            word_bank=request.word_bank,
            base_subreddit=request.query,
            before_start=request.before_start,
            before_end=request.before_end,
            after_start=request.after_start,
            after_end=request.after_end
        )
        
        return {
            "status": "success",
            "query": request.query,
            "before_summaries": results["before"],
            "after_summaries": results["after"],
            "before_stats": results["before_stats"],
            "after_stats": results["after_stats"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Before/after analysis failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)