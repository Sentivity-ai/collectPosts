import requests, pandas as pd
BASE = "https://collectposts.onrender.com"
def scrape(query, sources, limit=500, **kwargs):
    payload = {"query": query, "sources": sources, "limit_per_source": limit, **kwargs}
    r = requests.post(f"{BASE}/scrape-multi-source", json=payload, timeout=200)
    r.raise_for_status()
    meta = r.json()
    posts = meta.get("all_posts", meta.get("data", []))
    if not isinstance(posts, list):
        posts = [posts]
    df = pd.DataFrame(posts)
    return df, meta

if __name__ == "__main__":
    df, meta = scrape("Hamilton Beach", ["reddit", "youtube"], limit=1000, days=365)
    print(len(df), "posts found")
    # Set pandas display options to show the full DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df

