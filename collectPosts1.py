# collectPosts1.py (Final Version)
import os
import gradio as gr
import pandas as pd
import praw
import re
import matplotlib.pyplot as plt
import requests
import random
import joblib
import scipy.sparse as sp
from datetime import datetime, timedelta
from collections import defaultdict
from bs4 import BeautifulSoup
import instaloader
import tempfile
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from huggingface_hub import HfApi
import nltk
import os

nltk_data_path = "/home/user/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)
nltk.download("wordnet", download_dir=nltk_data_path)

# Ensure NLTK uses the downloaded directory
nltk.data.path.append(nltk_data_path)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID", "F9rgR81aVwJSjyB0cfqzLQ"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET", "jW9w9dSkntRzjlo2_S_HKRxaiSFgVw"),
    user_agent="sentivityb2c/0.1"
)

try:
    classifier = joblib.load('AutoClassifier.pkl')
    vectorizer = joblib.load("AutoVectorizer.pkl")
    FILTERING_ENABLED = True
except:
    FILTERING_ENABLED = False

def clean_text(text):
    return text.replace("\n", " ").strip() if isinstance(text, str) else ""

def collect_reddit_posts(subreddit_name="politics", time_period_days=30, limit=100):
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        cutoff = (datetime.utcnow() - timedelta(days=time_period_days)).timestamp()
        for post in subreddit.top(time_filter='month', limit=limit):
            if post.created_utc >= cutoff:
                posts.append({
                    "source": "Reddit",
                    "title": clean_text(post.title),
                    "content": clean_text(post.selftext),
                    "author": post.author.name if post.author else "[deleted]",
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        print(f"Reddit error: {e}")
    return posts

def collect_quora_posts(query="politics", max_pages=1):
    posts = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(max_pages):
        url = f"https://www.quora.com/search?q={query}&type=question&page={page+1}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            questions = soup.select("a.q-box.qu-mb--tiny.qu-cursor--pointer")
            for q in questions:
                title = q.get_text(strip=True)
                href = q.get("href")
                if href and "/profile" not in href:
                    posts.append({
                        "source": "Quora",
                        "title": clean_text(title),
                        "content": "",
                        "author": "",
                        "url": f"https://quora.com{href}",
                        "score": "",
                        "created_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            print(f"Quora error: {e}")
    return posts

def collect_youtube_video_titles(query="politics", max_results=10):
    api_key = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
    posts = []
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": api_key
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            posts.append({
                "source": "YouTube",
                "title": clean_text(title),
                "content": "",
                "author": item["snippet"]["channelTitle"],
                "url": url,
                "score": "",
                "created_utc": item["snippet"]["publishedAt"]
            })
    except Exception as e:
        print(f"YouTube error: {e}")
    return posts

reddit_posts = collect_reddit_posts("politics", 30, 100)
quora_posts = collect_quora_posts("politics", 1)
youtube_posts = collect_youtube_video_titles("politics", 10)

all_posts = reddit_posts + quora_posts + youtube_posts
df = pd.DataFrame(all_posts)
df.to_csv("politics_posts.csv", index=False)
print("\u2705 Saved to politics_posts.csv")

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    return re.sub(r'[^a-z\s]', '', text)

def generate_hashtags(posts):
    texts = [preprocess_text(p["title"] + " " + p.get("content", "")) for p in posts]
    vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
    X = vectorizer.fit_transform(texts)
    words = vectorizer.get_feature_names_out()
    scores = X.sum(axis=0).A1
    tags = [f"#{w}" for w, _ in sorted(zip(words, scores), key=lambda x: x[1], reverse=True)]
    for word in words:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                tag = f"#{lemma.name().lower().replace('_','')}"
                if tag not in tags:
                    tags.append(tag)
    tags += ["#trending1", "#viralnow", "#foryou"]
    return sorted(set(tags))[:50]

def upload_dataframe_to_hf(df, repo_id, filename="df.csv"):
    try:
        hf_token = os.getenv("hf_token")
        if not hf_token:
            return "\u274c No HF_TOKEN set"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            path = tmp.name
        HfApi().upload_file(
            path_or_fileobj=path,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="space",
            token=hf_token,
            commit_message=f"Update {filename} - {datetime.now()}"
        )
        os.unlink(path)
        return "\u2705 Uploaded to Hugging Face"
    except Exception as e:
        return f"\u274c Upload failed: {str(e)}"

def analyze(source, query, period):
    if source == "Reddit":
        posts = collect_reddit_posts(query)
    elif source == "Quora":
        posts = collect_quora_posts(query)
    elif source == "Instagram":
        posts = []  # Stub, implement if needed
    else:
        posts = []

    if not posts:
        return "No posts found.", [], ""

    hashtags = generate_hashtags(posts)
    df = pd.DataFrame(posts)
    df["date_only"] = datetime.utcnow().strftime('%Y-%m-%d')
    df["hashtags"] = ", ".join(hashtags)
    return "\u2705 Analysis complete", df, "\n".join(hashtags)

def create_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Social Hashtag Analyzer")
        source = gr.Dropdown(label="Source", choices=["Reddit", "Quora", "Instagram"], value="Reddit")
        query = gr.Textbox(label="Subreddit / Keyword / Hashtag")
        period = gr.Dropdown(choices=["Past Day", "Past Week", "Past Month", "Past 3 Months", "Past Year"], label="Time Range", value="Past Month")
        repo_id = gr.Textbox(label="HF Repo (e.g. user/myspace)")
        analyze_btn = gr.Button("Analyze")
        upload_btn = gr.Button("Upload to Hugging Face")
        status = gr.Textbox(label="Status")
        hashtags_md = gr.Textbox(label="Hashtags")
        df_out = gr.Dataframe()
        analyze_btn.click(analyze, [source, query, period], [status, df_out, hashtags_md])
        upload_btn.click(fn=lambda df, repo: upload_dataframe_to_hf(df, repo), inputs=[df_out, repo_id], outputs=[status])
    return demo

if __name__ == '__main__':
    demo = create_gradio_interface()
    demo.launch()
