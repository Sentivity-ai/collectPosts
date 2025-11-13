"""
Analysis Module - Core functionality for text analysis, clustering, and summarization
Based on HBWorkshop notebook implementation
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
from sentence_transformers import SentenceTransformer
import hdbscan
import joblib
import openai
from sklearn.cluster import KMeans
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from rapidfuzz import fuzz
from typing import List, Dict, Optional, Tuple

# Lazy loading for OpenAI client (only when needed)
_client = None
def get_openai_client():
    """Lazy load OpenAI client only when needed"""
    global _client
    if _client is None:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            return None
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client

# Lazy loading for classifier and vectorizer (only when needed)
_classifier = None
_vectorizer = None
FILTERING_ENABLED = False

def get_classifier():
    """Lazy load classifier only when needed"""
    global _classifier, _vectorizer, FILTERING_ENABLED
    if _classifier is None:
        try:
            _classifier = joblib.load('AutoClassifier.pkl')
            try:
                _vectorizer = joblib.load("AutoVectorizer.pkl")
            except:
                _vectorizer = None
            FILTERING_ENABLED = True
        except Exception as e:
            FILTERING_ENABLED = False
    return _classifier, _vectorizer

# Initialize embedder
_EMBEDDER = None
def get_embedder(name: str = 'all-MiniLM-L6-v2'):
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer(name)
    return _EMBEDDER

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Constants
MAX_TXTS_PER_CLUSTER = 50
POS_T = 0.30
NEG_T = -0.30

# Wish and mandatory word banks
WISH_WORD_BANK = [
    "nice to have", "would be nice", "i wish", "wish it had", "wish there was",
    "would love", "would be great", "great if", "better if", "if only",
    "would like", "i'd like", "i would like", "hoping for", "hope they add",
    "feature request", "wishlist", "optional", "bonus", "extra",
    "could use", "would appreciate", "ideally", "preferably", "looking for"
]

MANDATORY_CUES = [
    "must have", "dealbreaker", "deal breaker",
    "need this", "i need", "required", "require this",
    "can't use without", "cant use without", "cannot use without",
    "won't buy without", "wont buy without"
]

wish_wb = [w.lower() for w in WISH_WORD_BANK]
mandatory_wb = [w.lower() for w in MANDATORY_CUES]

# Compile regex patterns for wish detection
wish_pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in wish_wb) + r')\b', re.IGNORECASE)
mandatory_pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in mandatory_wb) + r')\b', re.IGNORECASE)


def preprocess_text(text: str) -> str:
    """Preprocess text for analysis"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'[^a-z0-9\s.,!?]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def vader_score(text: str) -> float:
    """Returns the VADER compound sentiment score for a given text."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return analyzer.polarity_scores(text)['compound']


def fuzzy_hit(s: str, word_bank: List[str], thresh: int = 70) -> bool:
    """Check if text matches any word in word bank using fuzzy matching"""
    s = str(s).lower()
    score = max(
        max(fuzz.token_set_ratio(s, w), fuzz.partial_ratio(s, w))
        for w in word_bank
    )
    return score >= thresh


def fuzzy_hit_wish(s: str, thresh: int = 70) -> bool:
    """Check if text expresses a wish/nice-to-have (not mandatory)"""
    s = str(s).lower()
    wish_score = max(max(fuzz.token_set_ratio(s, w), fuzz.partial_ratio(s, w)) for w in wish_wb)
    mandatory_score = max(max(fuzz.token_set_ratio(s, w), fuzz.partial_ratio(s, w)) for w in mandatory_wb)
    return wish_score >= thresh and mandatory_score < thresh


def is_pop_culture_choice(choice: str, no_pop_filter: bool = False) -> bool:
    """Check if choice indicates pop culture filtering"""
    if no_pop_filter:
        return False
    return isinstance(choice, str) and choice.strip().lower().startswith("pop")


def get_combined_recent_discourse(
    base_subreddit: str,
    df_local: pd.DataFrame,
    vectorizer_param=None,
    classifier_param=None,
    pop_culture: bool = True,
    no_pop_filter: bool = False
) -> pd.DataFrame:
    """Filter df_local by topic mask and optional classifier."""
    if df_local.empty:
        return df_local

    # Build a 'text' column once
    if 'text' not in df_local.columns:
        title = df_local.get('title', pd.Series("", index=df_local.index)).astype(str)
        content = df_local.get('content', pd.Series("", index=df_local.index)).astype(str)
        df_local = df_local.copy()
        df_local['text'] = (title + ' ' + content).str.strip()

    filtered_df = df_local.copy()

    if filtered_df.empty:
        return filtered_df

    # Apply classifier filtering if enabled
    if classifier_param is None or vectorizer_param is None:
        classifier_param, vectorizer_param = get_classifier()
    if (not no_pop_filter) and classifier_param is not None and vectorizer_param is not None:
        X = vectorizer_param.transform(filtered_df['text'])
        predictions = classifier_param.predict(X)
        keep_label = 0 if pop_culture else 1
        filtered_df = filtered_df[predictions == keep_label].copy()

    # Normalize timestamps → created_utc
    if 'created_utc' in filtered_df.columns:
        filtered_df['created_utc'] = pd.to_datetime(filtered_df['created_utc'], errors='coerce', utc=True)
        m = filtered_df['created_utc'].isna()
        if m.any():
            filtered_df.loc[m, 'created_utc'] = pd.to_datetime(
                filtered_df.loc[m, 'created_utc'], errors='coerce', format='%m/%d/%Y %H:%M', utc=True
            )
    elif 'upload_date' in filtered_df.columns:
        filtered_df['created_utc'] = pd.to_datetime(filtered_df['upload_date'], errors='coerce', utc=True)
    else:
        filtered_df['created_utc'] = pd.Timestamp.now(tz='UTC')

    return filtered_df


def cluster_texts_from_df(
    df: pd.DataFrame,
    min_cluster_size: int = 5,
    min_samples: Optional[int] = None,
    text_col: str = "text",
    model_name: str = 'all-MiniLM-L6-v2',
    batch_size: int = 32,
    normalize: bool = True
) -> Tuple[pd.DataFrame, Dict[int, List[str]]]:
    """Cluster texts in dataframe using HDBSCAN"""
    if df.empty or text_col not in df.columns:
        return df.assign(cluster_label=-1), {}

    texts_series = df[text_col].astype(str).str.strip()

    # Filter texts by length and token count
    len_mask = texts_series.str.len() >= 5
    tok_mask = texts_series.str.split().str.len() >= 3
    mask = len_mask & tok_mask

    if not mask.any():
        return df.assign(cluster_label=-1), {}

    texts = texts_series[mask].tolist()
    idxs = df.index[mask].to_numpy()
    n = len(texts)

    if min_cluster_size is None:
        min_cluster_size = max(2, min(10, n // 10 or 2))
    else:
        min_cluster_size = min(min_cluster_size, max(2, n))

    print(f"[INFO] n_texts={n}, min_cluster_size={min_cluster_size}, min_samples={min_samples}")
    print(f"[INFO] Sending {len(texts)} posts to clustering out of {len(df)} total")

    embedder = get_embedder(model_name)
    embeddings = embedder.encode(
        [preprocess_text(t) for t in texts],
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=normalize
    )

    if min_samples is None:
        min_samples = max(1, min_cluster_size // 2)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples
    )
    raw_labels = clusterer.fit_predict(embeddings)

    # Fallback to KMeans if HDBSCAN returns all noise
    if (raw_labels == -1).all() and len(embeddings) >= 4:
        print("[INFO] HDBSCAN returned all noise; falling back to KMeans(k=2).")
        km = KMeans(n_clusters=2, n_init=10, random_state=0)
        raw_labels = km.fit_predict(embeddings)

    labels_full = np.full(len(df), -1, dtype=int)
    labels_full[df.index.get_indexer(idxs)] = raw_labels
    cluster_df_local = df.copy()
    cluster_df_local["cluster_label"] = labels_full

    clusters_local = {}
    for t, lbl in zip(texts, raw_labels):
        clusters_local.setdefault(lbl, []).append(t)

    return cluster_df_local, clusters_local


def naive_count_proper_nouns(texts_list: List[str]) -> int:
    """Count proper nouns in a list of texts"""
    pat = re.compile(r'\b[A-Z][a-z]+\b')
    count = 0
    for text in texts_list:
        if not isinstance(text, str):
            continue
        count += len(pat.findall(text))
    return count


def generate_summary(cluster_texts: List[str], product_name: str) -> str:
    """Generate summary for a cluster using OpenAI"""
    if client is None:
        return "OpenAI API key not configured. Cannot generate summary."

    prompt = f"""\
Generate a concise report summarizing consumer feedback on {product_name} using the excerpts below.

Focus on:

Key Feedback: Main themes, opinions, and repeated points about product performance or quality.

Features Mentioned: Specific functions, materials, or design details noted by users.

Usage Context: Situations, settings, or activities where the product is discussed or used.

Insights: What this feedback implies about consumer expectations, satisfaction, or desired improvements.

Guidelines:

Only discuss feedback directly tied to {product_name}.

Highlight concrete mentions of features, quality, or experience — avoid general sentiment words.

Write in a neutral, analytical tone suitable for a short executive summary.

Keep the output brief - using bullet points to concisely output feedback

Do not reference data sources, social media, or clusters.

Excerpts:
{" ".join(cluster_texts)}
Generate the summary in the specified format:
"""
    client = get_openai_client()
    if client is None:
        return "OpenAI API key not configured. Cannot generate summary."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an analyst preparing a briefing on {product_name}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def generate_header(cluster_texts: List[str], base_subreddit: str) -> str:
    """Generate header for a cluster using OpenAI"""
    client = get_openai_client()
    if client is None:
        return "OpenAI API key not configured. Cannot generate header."

    prompt = f"""\
Based on the excerpts, generate a concise Title Case headline for a trend report on: {base_subreddit}.
Rules:
- Must relate to {base_subreddit}
- Include a clear verb (e.g., surge, popularize, trend, showcase)
- Reference key venues or locations if present
- No vague language
- Do not mention social media, Reddit, or clustering

Excerpts:
{" ".join(cluster_texts)}
Headline:
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a trend reporter writing concise titles about {base_subreddit}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error generating header: {str(e)}"


def summarize_clusters(proper_counts: Dict[int, int], clusters_param: Dict[int, List[str]], base_subreddit: str) -> str:
    """Summarize clusters sorted by proper noun count"""
    if not proper_counts:
        return "No valid clusters found."
    top_clusters = sorted(proper_counts, key=proper_counts.get, reverse=True)
    out = [f"### Trend Brief — {base_subreddit}"]
    for idx, cid in enumerate(top_clusters, 1):
        ctexts = clusters_param[cid][:MAX_TXTS_PER_CLUSTER]
        header = generate_header(ctexts, base_subreddit)
        summary = generate_summary(ctexts, base_subreddit)
        out.append(f"#### {idx}. {header}\n\n{summary}\n")
    return "\n---\n\n".join(out)


def summarize_basesubreddit_wrapper(
    posts_df: pd.DataFrame,
    base_subreddit: str,
    min_cluster_size: int = 3,
    min_samples: Optional[int] = None
) -> Tuple[str, Dict[int, List[str]]]:
    """Wrapper for clustering and summarization"""
    clustered_df, clusters_local = cluster_texts_from_df(posts_df, min_cluster_size, min_samples)
    proper_counts = {
        cid: naive_count_proper_nouns(txts)
        for cid, txts in clusters_local.items()
        if cid != -1
    }
    return summarize_clusters(proper_counts, clusters_local, base_subreddit=base_subreddit), clusters_local


def label_four_bins(df: pd.DataFrame, text_col: str = "text", pos_t: float = POS_T, neg_t: float = NEG_T) -> pd.DataFrame:
    """Label dataframe into four bins: love, hate, love|wish, hate|wish"""
    df = df.copy()
    
    # Ensure text column exists
    if text_col not in df.columns:
        title = df.get('title', pd.Series("", index=df.index)).astype(str)
        content = df.get('content', pd.Series("", index=df.index)).astype(str)
        df[text_col] = (title + " " + content).str.strip()
    
    # Calculate sentiment and wish flags
    df["is_wish"] = df[text_col].apply(fuzzy_hit_wish)
    df["vader_score"] = df[text_col].astype(str).map(vader_score)
    df["love"] = df["vader_score"] >= pos_t
    df["hate"] = df["vader_score"] <= neg_t

    def _four_bin(row):
        if row["hate"] and row["is_wish"]:
            return "hate|wish"
        if row["love"] and row["is_wish"]:
            return "love|wish"
        if row["hate"]:
            return "hate"
        if row["love"]:
            return "love"
        return "neutral"

    df["bin"] = df.apply(_four_bin, axis=1)
    return df


def summarize_one_bin(
    df_bin: pd.DataFrame,
    base_subreddit: str,
    min_cluster_size: int = 5,
    min_samples: Optional[int] = None,
    text_col: str = "text"
) -> Tuple[str, Dict[int, List[str]]]:
    """Summarize one bin (love/hate/wish)"""
    if df_bin.empty:
        return "No posts in this bin.", {}

    clustered_df, clusters_local = cluster_texts_from_df(
        df_bin, min_cluster_size=min_cluster_size, min_samples=min_samples, text_col=text_col
    )
    
    proper_counts = {
        cid: naive_count_proper_nouns(txts)
        for cid, txts in clusters_local.items()
        if cid != -1
    }
    
    if not proper_counts:
        return "No dense clusters found.", clusters_local

    top_clusters = sorted(proper_counts, key=proper_counts.get, reverse=True)
    parts = []
    for idx, cid in enumerate(top_clusters, 1):
        ctexts = clusters_local[cid][:MAX_TXTS_PER_CLUSTER]
        header = generate_header(ctexts, base_subreddit)
        summary = generate_summary(ctexts, base_subreddit)
        parts.append(f"#### {idx}. {header}\n\n{summary}\n")
    
    return "\n---\n\n".join(parts), clusters_local


def _summaries_for_dataset(df_in: pd.DataFrame, base_subreddit: str) -> Tuple[Dict[str, str], Dict[str, Dict[int, List[str]]]]:
    """
    Returns summaries for bins: love, hate, wish (wish combines 'hate|wish' + 'love|wish').
    """
    bins_map = {
        "love": df_in.loc[df_in["bin"] == "love", ["text"]].copy() if "text" in df_in.columns else pd.DataFrame(),
        "hate": df_in.loc[df_in["bin"] == "hate", ["text"]].copy() if "text" in df_in.columns else pd.DataFrame(),
        "wish": df_in.loc[df_in["bin"].isin(["hate|wish", "love|wish"]), ["text"]].copy() if "text" in df_in.columns else pd.DataFrame(),
    }

    summaries_by_bin = {}
    clusters_by_bin = {}

    for b, df_b in bins_map.items():
        if df_b.empty:
            summaries_by_bin[b] = "No posts in this bin."
            clusters_by_bin[b] = {}
            continue

        clustered_df, clusters_local = cluster_texts_from_df(
            df_b, min_cluster_size=5, min_samples=None, text_col="text"
        )
        clusters_by_bin[b] = clusters_local

        proper_counts = {
            cid: naive_count_proper_nouns(txts)
            for cid, txts in clusters_local.items()
            if cid != -1
        }

        if not proper_counts:
            summaries_by_bin[b] = "No dense clusters found."
            continue

        parts = []
        for idx, cid in enumerate(sorted(proper_counts, key=proper_counts.get, reverse=True), 1):
            ctexts = list(clusters_local[cid][:MAX_TXTS_PER_CLUSTER]) if cid in clusters_local else []
            if not ctexts:
                continue
            header = generate_header(ctexts, base_subreddit)
            summary = generate_summary(ctexts, base_subreddit)
            parts.append(f"#### {idx}. {header}\n\n{summary}\n")

        summaries_by_bin[b] = "\n---\n\n".join(parts) if parts else "No dense clusters found."

    return summaries_by_bin, clusters_by_bin


def process_df_with_word_bank(
    df: pd.DataFrame,
    word_bank: List[str],
    text_col: str = "text",
    pos_t: float = POS_T,
    neg_t: float = NEG_T
) -> pd.DataFrame:
    """Process dataframe with word bank filtering and binning"""
    df = df.copy()
    
    # Ensure text column exists
    if text_col not in df.columns:
        title = df.get('title', pd.Series("", index=df.index)).astype(str)
        content = df.get('content', pd.Series("", index=df.index)).astype(str)
        df[text_col] = (title + " " + content).str.strip()
    
    # Preprocess and filter by word bank
    df[text_col] = df[text_col].apply(preprocess_text)
    wb = [w.lower() for w in word_bank]
    df = df[df[text_col].apply(lambda x: fuzzy_hit(x, wb))].copy()
    
    # Calculate sentiment and wish
    df["is_wish"] = df[text_col].apply(fuzzy_hit_wish)
    df["vader_score"] = df[text_col].astype(str).map(vader_score)
    
    # Label bins
    df = label_four_bins(df, text_col=text_col, pos_t=pos_t, neg_t=neg_t)
    
    return df

