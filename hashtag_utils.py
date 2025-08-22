import re
import os
import nltk
import requests
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import wordnet
from collections import Counter
import random

try:
    nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.download("wordnet", download_dir=nltk_data_path, quiet=True)
    nltk.data.path.append(nltk_data_path)
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_hashtags(posts: List[Dict], max_hashtags: int = 50) -> List[str]:
    if not posts:
        return []
    
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
        vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words='english',
            min_df=1,
            max_df=0.9
        )
        
        X = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        scores = X.sum(axis=0).A1
        
        word_scores = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)
        
        for word, score in word_scores:
            if len(word) > 2:
                hashtag = f"#{word}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        for word, score in word_scores[:20]:
            try:
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        tag = f"#{lemma.name().lower().replace('_', '')}"
                        if tag not in hashtags and len(tag) > 3:
                            hashtags.append(tag)
            except Exception as e:
                print(f"Warning: Error processing WordNet for '{word}': {e}")
                continue
        
        trending_tags = ["#trending", "#viral", "#foryou", "#trendingnow", "#viralnow"]
        for tag in trending_tags:
            if tag not in hashtags:
                hashtags.append(tag)
        
        hashtags = hashtags[:max_hashtags]
        
    except Exception as e:
        print(f"Error in hashtag generation: {e}")
        hashtags = ["#trending", "#viral", "#foryou"]
    
    return hashtags

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
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
    trending_tags = []
    
    trending_tags.extend([
        "#trending", "#viral", "#foryou", "#trendingnow", "#viralnow",
        "#fyp", "#explore", "#discover", "#popular", "#hot",
        "#new", "#latest", "#breaking", "#news", "#update"
    ])
    
    try:
        pass
    except Exception as e:
        print(f"Error fetching trending hashtags: {e}")
    
    return trending_tags

def apply_frequency_thresholding(hashtags: List[str], min_frequency: int = 2) -> List[str]:
    if not hashtags:
        return []
    
    hashtag_counts = Counter(hashtags)
    
    filtered_hashtags = [
        hashtag for hashtag, count in hashtag_counts.items() 
        if count >= min_frequency
    ]
    
    return filtered_hashtags

def filter_topic_relevance(hashtags: List[str], topic_keywords: List[str]) -> List[str]:
    if not hashtags or not topic_keywords:
        return hashtags
    
    relevant_hashtags = []
    topic_keywords_lower = [kw.lower() for kw in topic_keywords]
    
    for hashtag in hashtags:
        hashtag_clean = hashtag.lower().replace('#', '')
        
        if any(keyword in hashtag_clean for keyword in topic_keywords_lower):
            relevant_hashtags.append(hashtag)
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
    if not posts:
        return []
    
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
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=1,
            max_df=1.0,
            token_pattern=r'\b[a-z]{3,}\b'
        )
        
        X = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        scores = X.sum(axis=0).A1
        
        word_scores = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)
        
        for word, score in word_scores[:30]:
            if len(word) > 2:
                hashtag = f"#{word}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        if include_synonyms:
            for word, score in word_scores[:20]:
                try:
                    synonyms = get_wordnet_synonyms(word)
                    for synonym in synonyms[:3]:
                        tag = f"#{synonym}"
                        if tag not in hashtags and len(synonym) > 2:
                            hashtags.append(tag)
                except Exception as e:
                    print(f"Warning: Error processing WordNet for '{word}': {e}")
                    continue
        
        if include_trending:
            trending_tags = get_trending_hashtags()
            for tag in trending_tags:
                if tag not in hashtags:
                    hashtags.append(tag)
        
        if apply_thresholding:
            hashtags = apply_frequency_thresholding(hashtags, min_frequency=1)
        
        if topic_keywords:
            hashtags = filter_topic_relevance(hashtags, topic_keywords)
        
        hashtags = hashtags[:max_hashtags]
        
    except Exception as e:
        print(f"Error in enhanced hashtag generation: {e}")
        hashtags = ["#trending", "#viral", "#foryou"]
    
    return hashtags

def merge_hashtags_from_sources(
    reddit_hashtags: List[str] = None,
    quora_hashtags: List[str] = None,
    instagram_hashtags: List[str] = None,
    youtube_hashtags: List[str] = None
) -> List[str]:
    all_hashtags = []
    
    if reddit_hashtags:
        all_hashtags.extend(reddit_hashtags)
    if quora_hashtags:
        all_hashtags.extend(quora_hashtags)
    if instagram_hashtags:
        all_hashtags.extend(instagram_hashtags)
    if youtube_hashtags:
        all_hashtags.extend(youtube_hashtags)
    
    seen = set()
    unique_hashtags = []
    for hashtag in all_hashtags:
        if hashtag not in seen:
            seen.add(hashtag)
            unique_hashtags.append(hashtag)
    
    return unique_hashtags
