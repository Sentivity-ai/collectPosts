import re
from collections import Counter
from typing import List, Dict
import re

def clean_text(text: str) -> str:
    """Clean text for hashtag extraction"""
    if not text:
        return ""
    # Remove URLs, mentions, and special characters
    text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.lower().strip()

def extract_keywords(text: str, min_length: int = 3, max_length: int = 20) -> List[str]:
    """Extract keywords from text using simple frequency analysis"""
    if not text:
        return []
    
    # Clean the text
    clean = clean_text(text)
    
    # Split into words and filter
    words = clean.split()
    words = [w for w in words if min_length <= len(w) <= max_length]
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'a', 'an', 'i', 'you', 'he', 'she',
        'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
        'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'
    }
    
    # Filter out stop words and get word frequencies
    filtered_words = [w for w in words if w not in stop_words]
    word_counts = Counter(filtered_words)
    
    # Return most common words
    return [word for word, count in word_counts.most_common(20)]

def generate_hashtags_from_posts(posts: List[Dict], max_tags: int = 15) -> List[str]:
    """
    Generate hashtags from a list of posts using TF-IDF-like analysis
    
    Args:
        posts: List of post dictionaries with 'title' and 'content' fields
        max_tags: Maximum number of hashtags to return
    
    Returns:
        List of hashtag strings (e.g., ['#technology', '#ai', '#innovation'])
    """
    if not posts:
        return []
    
    # Combine all text from posts
    all_text = ""
    for post in posts:
        title = post.get('title', '')
        content = post.get('content', '')
        all_text += f" {title} {content}"
    
    # Extract keywords
    keywords = extract_keywords(all_text)
    
    # Convert to hashtags
    hashtags = []
    for keyword in keywords[:max_tags]:
        # Clean and format as hashtag
        hashtag = re.sub(r'[^\w]', '', keyword)
        if len(hashtag) > 1:  # Avoid single character hashtags
            hashtags.append(f"#{hashtag}")
    
    return hashtags

def generate_hashtags_by_source(posts: List[Dict], max_tags_per_source: int = 5) -> Dict[str, List[str]]:
    """
    Generate hashtags grouped by source
    
    Args:
        posts: List of post dictionaries
        max_tags_per_source: Maximum hashtags per source
    
    Returns:
        Dictionary mapping source names to lists of hashtags
    """
    source_hashtags = {}
    
    # Group posts by source
    posts_by_source = {}
    for post in posts:
        source = post.get('source', 'unknown')
        if source not in posts_by_source:
            posts_by_source[source] = []
        posts_by_source[source].append(post)
    
    # Generate hashtags for each source
    for source, source_posts in posts_by_source.items():
        hashtags = generate_hashtags_from_posts(source_posts, max_tags_per_source)
        source_hashtags[source] = hashtags
    
    return source_hashtags

def get_trending_hashtags(posts: List[Dict], time_window: str = "week") -> List[str]:
    """
    Get trending hashtags based on post frequency and recency
    
    Args:
        posts: List of post dictionaries
        time_window: Time window for trending analysis
    
    Returns:
        List of trending hashtag strings
    """
    if not posts:
        return []
    
    # Extract hashtags from post content
    all_hashtags = []
    for post in posts:
        content = post.get('content', '') + ' ' + post.get('title', '')
        hashtags = re.findall(r'#\w+', content)
        all_hashtags.extend(hashtags)
    
    # Count hashtag frequency
    hashtag_counts = Counter(all_hashtags)
    
    # Return most common hashtags
    return [hashtag for hashtag, count in hashtag_counts.most_common(10)]

# Example usage and testing
if __name__ == "__main__":
    # Test with sample posts
    sample_posts = [
        {
            "title": "AI Technology Revolution",
            "content": "Artificial intelligence is transforming industries with machine learning and automation",
            "source": "reddit"
        },
        {
            "title": "Machine Learning Trends",
            "content": "Deep learning and neural networks are advancing rapidly in 2024",
            "source": "youtube"
        }
    ]
    
    hashtags = generate_hashtags_from_posts(sample_posts)
    print("Generated hashtags:", hashtags)
    
    source_hashtags = generate_hashtags_by_source(sample_posts)
    print("Hashtags by source:", source_hashtags)
