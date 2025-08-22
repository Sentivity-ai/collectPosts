import re
import os
import nltk
import requests
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import wordnet
from collections import Counter
import random

# Download NLTK data
try:
    nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.download("wordnet", download_dir=nltk_data_path, quiet=True)
    nltk.data.path.append(nltk_data_path)
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

def preprocess_text(text: str) -> str:
    """
    Preprocess text for hashtag generation
    
    Args:
        text: Input text to preprocess
    
    Returns:
        Preprocessed text
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove special characters, keep only letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_hashtags(posts: List[Dict], max_hashtags: int = 50) -> List[str]:
    """
    Generate hashtags from a list of posts using TF-IDF and WordNet
    
    Args:
        posts: List of post dictionaries with 'title' and 'content' keys
        max_hashtags: Maximum number of hashtags to return
    
    Returns:
        List of generated hashtags
    """
    if not posts:
        return []
    
    # Extract and preprocess text from posts
    texts = []
    for post in posts:
        title = post.get("title", "")
        content = post.get("content", "")
        combined_text = f"{title} {content}"
        processed_text = preprocess_text(combined_text)
        if processed_text:
            texts.append(processed_text)
    
    if not texts:
        return []
    
    # Generate hashtags using TF-IDF
    hashtags = []
    
    try:
        # Use TF-IDF to find important words
        vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words='english',
            min_df=1,
            max_df=0.9
        )
        
        X = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        scores = X.sum(axis=0).A1
        
        # Sort words by TF-IDF score
        word_scores = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)
        
        # Add top words as hashtags
        for word, score in word_scores:
            if len(word) > 2:  # Filter out very short words
                hashtag = f"#{word}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        # Add WordNet synonyms for important words
        for word, score in word_scores[:20]:  # Top 20 words
            try:
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        tag = f"#{lemma.name().lower().replace('_', '')}"
                        if tag not in hashtags and len(tag) > 3:
                            hashtags.append(tag)
            except Exception as e:
                print(f"Warning: Error processing WordNet for '{word}': {e}")
                continue
        
        # Add some trending hashtags
        trending_tags = ["#trending", "#viral", "#foryou", "#trendingnow", "#viralnow"]
        for tag in trending_tags:
            if tag not in hashtags:
                hashtags.append(tag)
        
        # Limit the number of hashtags
        hashtags = hashtags[:max_hashtags]
        
    except Exception as e:
        print(f"Error in hashtag generation: {e}")
        # Fallback to simple hashtags
        hashtags = ["#trending", "#viral", "#foryou"]
    
    return hashtags

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using TF-IDF
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
    
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    processed_text = preprocess_text(text)
    if not processed_text:
        return []
    
    try:
        vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words='english',
            min_df=1
        )
        
        X = vectorizer.fit_transform([processed_text])
        words = vectorizer.get_feature_names_out()
        
        return list(words)
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []

def get_wordnet_synonyms(word: str) -> List[str]:
    """
    Get synonyms for a word using WordNet
    
    Args:
        word: Input word
    
    Returns:
        List of synonyms
    """
    synonyms = []
    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonym = lemma.name().lower().replace('_', '')
                if synonym != word and synonym not in synonyms:
                    synonyms.append(synonym)
    except Exception as e:
        print(f"Error getting synonyms for '{word}': {e}")
    
    return synonyms

def get_trending_hashtags() -> List[str]:
    """
    Get trending hashtags from various sources
    
    Returns:
        List of trending hashtags
    """
    trending_tags = []
    
    # Add some popular trending hashtags
    trending_tags.extend([
        "#trending", "#viral", "#foryou", "#trendingnow", "#viralnow",
        "#fyp", "#explore", "#discover", "#popular", "#hot",
        "#new", "#latest", "#breaking", "#news", "#update"
    ])
    
    # Try to get real trending hashtags (this would need API access)
    try:
        # You could integrate with services like:
        # - Twitter Trends API
        # - Instagram Trending API
        # - YouTube Trending API
        pass
    except Exception as e:
        print(f"Error fetching trending hashtags: {e}")
    
    return trending_tags

def apply_frequency_thresholding(hashtags: List[str], min_frequency: int = 2) -> List[str]:
    """
    Apply frequency thresholding to filter out low-occurrence hashtags
    
    Args:
        hashtags: List of hashtags
        min_frequency: Minimum frequency threshold
    
    Returns:
        Filtered list of hashtags
    """
    if not hashtags:
        return []
    
    # Count frequency
    hashtag_counts = Counter(hashtags)
    
    # Filter by frequency
    filtered_hashtags = [
        hashtag for hashtag, count in hashtag_counts.items() 
        if count >= min_frequency
    ]
    
    return filtered_hashtags

def filter_topic_relevance(hashtags: List[str], topic_keywords: List[str]) -> List[str]:
    """
    Filter hashtags for topic relevance
    
    Args:
        hashtags: List of hashtags
        topic_keywords: List of topic keywords
    
    Returns:
        Filtered list of relevant hashtags
    """
    if not hashtags or not topic_keywords:
        return hashtags
    
    relevant_hashtags = []
    topic_keywords_lower = [kw.lower() for kw in topic_keywords]
    
    for hashtag in hashtags:
        hashtag_clean = hashtag.lower().replace('#', '')
        
        # Check if hashtag contains any topic keywords
        if any(keyword in hashtag_clean for keyword in topic_keywords_lower):
            relevant_hashtags.append(hashtag)
        # Also check if it's a general trending tag
        elif hashtag in ["#trending", "#viral", "#foryou", "#fyp"]:
            relevant_hashtags.append(hashtag)
    
    return relevant_hashtags

def enhanced_generate_hashtags(
    posts: List[Dict], 
    max_hashtags: int = 50,
    include_synonyms: bool = True,
    include_trending: bool = True,
    apply_thresholding: bool = True,
    topic_keywords: List[str] = None
) -> List[str]:
    """
    Enhanced hashtag generation with advanced features
    
    Args:
        posts: List of post dictionaries
        max_hashtags: Maximum number of hashtags to return
        include_synonyms: Whether to include WordNet synonyms
        include_trending: Whether to include trending hashtags
        apply_thresholding: Whether to apply frequency thresholding
        topic_keywords: Keywords for topic relevance filtering
    
    Returns:
        List of generated hashtags
    """
    if not posts:
        return []
    
    # Extract and preprocess text from posts
    texts = []
    for post in posts:
        title = post.get("title", "")
        content = post.get("content", "")
        combined_text = f"{title} {content}"
        processed_text = preprocess_text(combined_text)
        if processed_text:
            texts.append(processed_text)
    
    if not texts:
        return []
    
    hashtags = []
    
    try:
        # Use TF-IDF to find important words
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=1,
            max_df=1.0,  # Allow all documents to contain a term
            token_pattern=r'\b[a-z]{3,}\b'  # Words with 3+ characters
        )
        
        X = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        scores = X.sum(axis=0).A1
        
        # Sort words by TF-IDF score
        word_scores = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)
        
        # Add top words as hashtags
        for word, score in word_scores[:30]:  # Top 30 words
            if len(word) > 2:  # Filter out very short words
                hashtag = f"#{word}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        # Add WordNet synonyms for important words
        if include_synonyms:
            for word, score in word_scores[:20]:  # Top 20 words
                try:
                    synonyms = get_wordnet_synonyms(word)
                    for synonym in synonyms[:3]:  # Limit to 3 synonyms per word
                        tag = f"#{synonym}"
                        if tag not in hashtags and len(synonym) > 2:
                            hashtags.append(tag)
                except Exception as e:
                    print(f"Warning: Error processing WordNet for '{word}': {e}")
                    continue
        
        # Add trending hashtags
        if include_trending:
            trending_tags = get_trending_hashtags()
            for tag in trending_tags:
                if tag not in hashtags:
                    hashtags.append(tag)
        
        # Apply frequency thresholding
        if apply_thresholding:
            hashtags = apply_frequency_thresholding(hashtags, min_frequency=1)
        
        # Filter for topic relevance
        if topic_keywords:
            hashtags = filter_topic_relevance(hashtags, topic_keywords)
        
        # Limit the number of hashtags
        hashtags = hashtags[:max_hashtags]
        
    except Exception as e:
        print(f"Error in enhanced hashtag generation: {e}")
        # Fallback to simple hashtags
        hashtags = ["#trending", "#viral", "#foryou"]
    
    return hashtags

def merge_hashtags_from_sources(
    reddit_hashtags: List[str] = None,
    quora_hashtags: List[str] = None,
    instagram_hashtags: List[str] = None,
    youtube_hashtags: List[str] = None
) -> List[str]:
    """
    Merge hashtags from all sources and remove duplicates
    
    Args:
        reddit_hashtags: Hashtags from Reddit
        quora_hashtags: Hashtags from Quora
        instagram_hashtags: Hashtags from Instagram
        youtube_hashtags: Hashtags from YouTube
    
    Returns:
        Merged and deduplicated list of hashtags
    """
    all_hashtags = []
    
    if reddit_hashtags:
        all_hashtags.extend(reddit_hashtags)
    if quora_hashtags:
        all_hashtags.extend(quora_hashtags)
    if instagram_hashtags:
        all_hashtags.extend(instagram_hashtags)
    if youtube_hashtags:
        all_hashtags.extend(youtube_hashtags)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_hashtags = []
    for hashtag in all_hashtags:
        if hashtag not in seen:
            seen.add(hashtag)
            unique_hashtags.append(hashtag)
    
    return unique_hashtags
