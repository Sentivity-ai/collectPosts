import os
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

def clean_text(text: str) -> str:
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def _chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def collect_youtube_video_titles(
    query: str = "politics",
    max_results: int = 100,
    time_period_days: int = 30,
    region_code: str | None = None,
    relevance_language: str | None = None,
    safe_search: str = "none",   # "none", "moderate", or "strict"
) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY env var is required")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    posts: List[Dict] = []
    next_page_token = None

    # Strict cutoff
    now = datetime.now(timezone.utc)
    cutoff_dt = now - timedelta(days=time_period_days)
    published_after = cutoff_dt.strftime(ISO8601)

    # YouTube Search: up to 50 per request
    remaining = max(1, max_results)
    while remaining > 0:
        per_page = min(50, remaining)
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": per_page,
            "key": api_key,
            "order": "date",  # ensure chronological
            "publishedAfter": published_after,
            "safeSearch": safe_search,
        }
        if region_code:
            params["regionCode"] = region_code
        if relevance_language:
            params["relevanceLanguage"] = relevance_language
        if next_page_token:
            params["pageToken"] = next_page_token

        res = requests.get(search_url, params=params, timeout=15)
        data = res.json()
        if "error" in data:
            raise RuntimeError(f"YouTube API error: {data['error'].get('message', 'Unknown error')}")

        items = data.get("items", [])
        if not items:
            break  # no more

        video_ids = []
        prelim_rows = []
        for it in items:
            vid = it.get("id", {}).get("videoId")
            sn = it.get("snippet", {})
            if not vid:
                continue
            # Parse publishedAt and enforce cutoff client-side too (belt & suspenders)
            try:
                pub_dt = datetime.strptime(sn.get("publishedAt", ""), ISO8601).replace(tzinfo=timezone.utc)
            except Exception:
                pub_dt = now  # if missing, keep it (rare)

            if pub_dt < cutoff_dt:
                continue

            video_ids.append(vid)
            prelim_rows.append({
                "id": vid,
                "source": "YouTube",
                "title": clean_text(sn.get("title", "")),
                "content": clean_text(sn.get("description", "")),
                "author": sn.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "created_utc": sn.get("publishedAt", pub_dt.strftime(ISO8601)),
            })

        # Enrich with statistics (views/likes) using videos.list (50 ids per call)
        stats_by_id: dict[str, dict] = {}
        for chunk_ids in _chunk(video_ids, 50):
            v_params = {
                "part": "statistics",
                "id": ",".join(chunk_ids),
                "key": api_key,
            }
            v_res = requests.get(videos_url, params=v_params, timeout=15)
            v_data = v_res.json()
            for v in v_data.get("items", []):
                vid = v.get("id")
                stats_by_id[vid] = v.get("statistics", {}) if vid else {}

        # Build rows with a meaningful score (views)
        for row in prelim_rows:
            stats = stats_by_id.get(row["id"], {})
            view_count = int(stats.get("viewCount", 0)) if stats else 0
            row["score"] = view_count
            posts.append(row)

        remaining = max_results - len(posts)
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    # Trim to max_results just in case
    return posts[:max_results]
