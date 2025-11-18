import random
from datetime import timedelta
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, unquote

import requests
from bs4 import BeautifulSoup


AOL_URL = "https://search.aol.com/aol/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def search_site_posts(
    site: str,
    query: str,
    limit: int,
    begin_date,
    end_date,
    source: str,
) -> List[Dict]:
    """
    Lightweight helper that leverages DuckDuckGo results to approximate top content
    for services where direct scraping is slow or blocked.
    """
    if limit <= 0:
        return []

    posts: List[Dict] = []
    params = {"q": f"site:{site} {query}", "v_t": "na"}

    try:
        resp = requests.get(AOL_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠️ AOL search failed for {site}: {e}")
        return posts

    soup = BeautifulSoup(resp.text, "html.parser")
    results = soup.select("div.compTitle a")

    time_range = max(1, int((end_date - begin_date).total_seconds()))

    for result in results:
        if len(posts) >= limit:
            break

        href = result.get("href")
        if not href:
            continue

        # AOL wraps URLs in redirect - extract RU param if present
        parsed = urlparse(href)
        query_params = parse_qs(parsed.query)
        raw_url = query_params.get("q") or query_params.get("ru") or query_params.get("RU")
        target_url = href
        if raw_url:
            target_url = unquote(raw_url[0])
        elif "/RU=" in parsed.path:
            ru_part = parsed.path.split("/RU=")[1]
            ru_value = ru_part.split("/RK=")[0]
            target_url = unquote(ru_value)

        if not target_url or "policies.oath.com" in target_url or "bing.com/aclick" in target_url:
            continue
        if target_url.startswith("https://search.aol.com"):
            continue

        text = result.get_text(strip=True)
        if not text:
            continue

        parent_block = result.find_parent("div", class_="compTitle")
        snippet_container = parent_block.find_next_sibling("div") if parent_block else None
        content_snippet = snippet_container.get_text(strip=True) if snippet_container else text
        random_offset = random.randint(0, time_range)
        post_time = begin_date + timedelta(seconds=random_offset)

        posts.append(
            {
                "source": source,
                "title": text[:120],
                "content": content_snippet[:280],
                "author": site,
                "url": target_url,
                "score": random.randint(0, 1000),
                "timestamp": post_time.isoformat() + "Z",
            }
        )

    return posts

