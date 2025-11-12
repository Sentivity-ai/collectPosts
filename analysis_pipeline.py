"""
Analysis Pipeline - Main pipeline for before/after analysis
Based on HBWorkshop notebook implementation
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, List, Optional
from analysis import (
    process_df_with_word_bank,
    _summaries_for_dataset,
    label_four_bins,
    preprocess_text,
    fuzzy_hit,
    vader_score,
    POS_T,
    NEG_T,
    wish_wb,
    mandatory_wb
)


def analyze_before_after(
    data: pd.DataFrame,
    word_bank: List[str],
    base_subreddit: str,
    before_start: str,
    before_end: str,
    after_start: str,
    after_end: str,
    date_col: str = "date_only"
) -> Dict[str, Dict[str, str]]:
    """
    Analyze data before and after a launch date
    
    Args:
        data: DataFrame with posts
        word_bank: List of words to filter by
        base_subreddit: Product/subreddit name for summaries
        before_start: Start date for before period (YYYY-MM-DD)
        before_end: End date for before period (YYYY-MM-DD)
        after_start: Start date for after period (YYYY-MM-DD)
        after_end: End date for after period (YYYY-MM-DD)
        date_col: Name of date column
    
    Returns:
        Dictionary with summaries for before/after periods
    """
    # Ensure date column is datetime
    if date_col not in data.columns:
        # Try to find a date column
        for col in ['created_utc', 'upload_date', 'published', 'datetime']:
            if col in data.columns:
                date_col = col
                break
        else:
            raise ValueError(f"No date column found. Available columns: {data.columns.tolist()}")
    
    data[date_col] = pd.to_datetime(data[date_col])
    
    # Filter datasets
    data_in_before = data[
        (data[date_col] >= before_start) & (data[date_col] < before_end)
    ].copy()
    
    data_in_after = data[
        (data[date_col] >= after_start) & (data[date_col] < after_end)
    ].copy()
    
    # Process both datasets
    for df_name, df in [("before", data_in_before), ("after", data_in_after)]:
        # Ensure text column exists
        if 'text' not in df.columns:
            title = df.get('title', pd.Series("", index=df.index)).astype(str)
            content = df.get('content', pd.Series("", index=df.index)).astype(str)
            df['text'] = (title + ' ' + content).str.strip()
        
        # Preprocess and filter
        df['text'] = df['text'].apply(preprocess_text)
        wb = [w.lower() for w in word_bank]
        df = df[df['text'].apply(lambda x: fuzzy_hit(x, wb))].copy()
        
        # Calculate sentiment
        df['vader_score'] = df['text'].astype(str).map(vader_score)
        
        # Keep only needed columns
        df = df[['text', 'vader_score']].copy()
        
        # Assign back
        if df_name == "before":
            data_in_before = df
        else:
            data_in_after = df
    
    # Label bins
    data_in_before = label_four_bins(data_in_before, text_col="text", pos_t=POS_T, neg_t=NEG_T)
    data_in_after = label_four_bins(data_in_after, text_col="text", pos_t=POS_T, neg_t=NEG_T)
    
    # Generate summaries
    summaries_before, clusters_before = _summaries_for_dataset(data_in_before, base_subreddit)
    summaries_after, clusters_after = _summaries_for_dataset(data_in_after, base_subreddit)
    
    return {
        "before": summaries_before,
        "after": summaries_after,
        "before_clusters": clusters_before,
        "after_clusters": clusters_after,
        "before_stats": {
            "total": len(data_in_before),
            "love": len(data_in_before[data_in_before["bin"] == "love"]),
            "hate": len(data_in_before[data_in_before["bin"] == "hate"]),
            "wish": len(data_in_before[data_in_before["bin"].isin(["hate|wish", "love|wish"])])
        },
        "after_stats": {
            "total": len(data_in_after),
            "love": len(data_in_after[data_in_after["bin"] == "love"]),
            "hate": len(data_in_after[data_in_after["bin"] == "hate"]),
            "wish": len(data_in_after[data_in_after["bin"].isin(["hate|wish", "love|wish"])])
        }
    }


def cluster_and_summarize(
    posts_df: pd.DataFrame,
    base_subreddit: str,
    min_cluster_size: int = 5,
    min_samples: Optional[int] = None,
    word_bank: Optional[List[str]] = None,
    pop_culture: bool = True,
    no_pop_filter: bool = False
) -> Tuple[str, Dict[int, List[str]]]:
    """
    Cluster and summarize posts
    
    Args:
        posts_df: DataFrame with posts
        base_subreddit: Product/subreddit name
        min_cluster_size: Minimum cluster size
        min_samples: Minimum samples for clustering
        word_bank: Optional word bank for filtering
        pop_culture: Whether to filter for pop culture
        no_pop_filter: Whether to disable pop culture filter
    
    Returns:
        Tuple of (summary_text, clusters_dict)
    """
    from analysis import (
        get_combined_recent_discourse,
        summarize_basesubreddit_wrapper,
        is_pop_culture_choice,
        classifier,
        vectorizer
    )
    
    # Filter by topic + content type
    pop_culture_flag = is_pop_culture_choice("pop" if pop_culture else "", no_pop_filter)
    filtered_df = get_combined_recent_discourse(
        base_subreddit,
        df_local=posts_df,
        vectorizer_param=vectorizer,
        classifier_param=classifier,
        pop_culture=pop_culture_flag,
        no_pop_filter=no_pop_filter
    )
    
    if filtered_df.empty:
        return "No discourse found (after filtering) for your selections.", {}
    
    # Apply word bank filtering if provided
    if word_bank:
        filtered_df = process_df_with_word_bank(filtered_df, word_bank)
    
    # Cluster + summarize
    summary_text, clusters = summarize_basesubreddit_wrapper(
        filtered_df, base_subreddit, min_cluster_size, min_samples
    )
    
    return summary_text, clusters

