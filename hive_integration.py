import os
import pandas as pd
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from huggingface_hub import HfApi
import tempfile
import math
import numpy as np

class HiveIntegration:
    def __init__(self, hive_space_url: str = None, hf_token: str = None):
        self.hive_space_url = hive_space_url or os.getenv("HIVE_SPACE_URL", "https://huggingface.co/spaces/sentivity/topicfinder")
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        
    def create_headlines_csv(self, posts: List[Dict], filename: str = None) -> str:
        """Create a CSV optimized for Hive headline generation"""
        if not posts:
            return "❌ No posts to process"
            
        # Structure data for headline generation
        headlines_data = []
        
        for post in posts:
            # Extract key information for headline generation
            headline_row = {
                'source': post.get('source', ''),
                'title': post.get('title', ''),
                'content': post.get('content', ''),
                'author': post.get('author', ''),
                'score': post.get('score', 0),
                'url': post.get('url', ''),
                'timestamp': post.get('timestamp', ''),
                'engagement_score': self._calculate_engagement_score(post),
                'sentiment_keywords': self._extract_sentiment_keywords(post),
                'topic_category': self._categorize_topic(post),
                'viral_potential': self._assess_viral_potential(post)
            }
            headlines_data.append(headline_row)
        
        # Create DataFrame
        df = pd.DataFrame(headlines_data)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"headlines_data_{timestamp}.csv"
        
        # Save to CSV
        csv_path = f"./outputs/{filename}"
        os.makedirs("./outputs", exist_ok=True)
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    def _calculate_engagement_score(self, post: Dict) -> float:
        """Calculate engagement score based on post metrics"""
        # Convert to numbers, handling string inputs
        try:
            score = float(post.get('score', 0))
        except (ValueError, TypeError):
            score = 0.0
            
        try:
            comments = float(post.get('num_comments', 0))
        except (ValueError, TypeError):
            comments = 0.0
            
        try:
            upvotes = float(post.get('upvote_ratio', 0.5))
        except (ValueError, TypeError):
            upvotes = 0.5
        
        # Weighted engagement score
        engagement = (score * 0.4) + (comments * 0.4) + (upvotes * 0.2)
        return round(engagement, 2)
    
    def _extract_sentiment_keywords(self, post: Dict) -> str:
        """Extract sentiment-indicating keywords"""
        content = (post.get('title', '') + ' ' + post.get('content', '')).lower()
        
        positive_words = ['amazing', 'incredible', 'awesome', 'great', 'excellent', 'fantastic', 'wonderful']
        negative_words = ['terrible', 'awful', 'horrible', 'disgusting', 'shocking', 'outrageous', 'scandalous']
        viral_words = ['viral', 'trending', 'breaking', 'exclusive', 'shocking', 'controversial', 'explosive']
        
        keywords = []
        for word in positive_words + negative_words + viral_words:
            if word in content:
                keywords.append(word)
        
        return ', '.join(keywords[:5])  # Limit to top 5 keywords
    
    def _categorize_topic(self, post: Dict) -> str:
        """Categorize post topic for headline generation"""
        content = (post.get('title', '') + ' ' + post.get('content', '')).lower()
        
        categories = {
            'politics': ['politics', 'election', 'president', 'congress', 'democrat', 'republican', 'vote'],
            'technology': ['tech', 'technology', 'ai', 'artificial intelligence', 'software', 'app', 'startup'],
            'entertainment': ['movie', 'film', 'celebrity', 'actor', 'actress', 'music', 'concert', 'award'],
            'sports': ['sport', 'football', 'basketball', 'baseball', 'soccer', 'championship', 'team'],
            'business': ['business', 'company', 'stock', 'market', 'economy', 'finance', 'investment'],
            'health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'treatment', 'vaccine']
        }
        
        for category, keywords in categories.items():
            if any(keyword in content for keyword in keywords):
                return category
        
        return 'general'
    
    def _assess_viral_potential(self, post: Dict) -> str:
        """Assess viral potential for headline optimization"""
        engagement = self._calculate_engagement_score(post)
        content = (post.get('title', '') + ' ' + post.get('content', '')).lower()
        
        viral_indicators = ['viral', 'trending', 'breaking', 'exclusive', 'shocking', 'controversial']
        has_viral_words = any(word in content for word in viral_indicators)
        
        if engagement > 1000 or has_viral_words:
            return 'high'
        elif engagement > 100:
            return 'medium'
        else:
            return 'low'
    
    def _clean_for_json(self, data):
        """Clean data to ensure JSON compatibility"""
        if isinstance(data, dict):
            return {k: self._clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_json(item) for item in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return 0.0
            return data
        elif isinstance(data, (int, str, bool, type(None))):
            return data
        else:
            return str(data)

    def send_to_hive(self, csv_path: str, hive_endpoint: str = None) -> str:
        """Send CSV data to Hive service for headline generation"""
        try:
            if not os.path.exists(csv_path):
                return f"❌ CSV file not found: {csv_path}"
            
            # Read CSV data
            df = pd.read_csv(csv_path)
            
            # Clean the data to ensure JSON compatibility
            df_clean = df.copy()
            for col in df_clean.select_dtypes(include=[np.number]).columns:
                df_clean[col] = df_clean[col].replace([np.inf, -np.inf], 0.0)
                df_clean[col] = df_clean[col].fillna(0.0)
            
            # Prepare data for Hive
            hive_data = {
                'posts': df_clean.to_dict('records'),
                'metadata': {
                    'total_posts': len(df_clean),
                    'sources': df_clean['source'].unique().tolist(),
                    'topics': df_clean['topic_category'].unique().tolist(),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Clean the entire data structure for JSON
            hive_data = self._clean_for_json(hive_data)
            
            # Send to Hive endpoint
            endpoint = hive_endpoint or f"{self.hive_space_url}/api/predict"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.hf_token}' if self.hf_token else None
            }
            
            response = requests.post(
                endpoint,
                json=hive_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"✅ Successfully sent to Hive. Generated {len(result.get('headlines', []))} headlines"
            else:
                return f"❌ Hive API error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Failed to send to Hive: {str(e)}"
    
    def upload_to_hf_dataset(self, csv_path: str, repo_id: str, filename: str = None) -> str:
        """Upload CSV to Hugging Face dataset for Hive processing"""
        try:
            if not self.hf_token:
                return "❌ No HF_TOKEN environment variable set"
            
            if not filename:
                filename = os.path.basename(csv_path)
            
            api = HfApi()
            
            # Try to create the repository if it doesn't exist
            try:
                api.create_repo(
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=self.hf_token,
                    exist_ok=True,
                    private=False
                )
                print(f"✅ Repository {repo_id} created/verified successfully")
            except Exception as create_error:
                print(f"⚠️ Repository creation warning: {create_error}")
                # Continue anyway, the upload might still work
            
            # Upload the file
            api.upload_file(
                path_or_fileobj=csv_path,
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type="dataset",
                token=self.hf_token,
                commit_message=f"Upload headlines data for Hive processing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return f"✅ Successfully uploaded {filename} to {repo_id} for Hive processing"
            
        except Exception as e:
            return f"❌ Upload failed: {str(e)}"
    
    def generate_headlines_summary(self, posts: List[Dict]) -> Dict:
        """Generate summary statistics for headline optimization"""
        if not posts:
            return {}
        
        # Create DataFrame with all required fields
        headlines_data = []
        for post in posts:
            headline_row = {
                'source': post.get('source', ''),
                'title': post.get('title', ''),
                'content': post.get('content', ''),
                'author': post.get('author', ''),
                'score': post.get('score', 0),
                'url': post.get('url', ''),
                'timestamp': post.get('timestamp', ''),
                'engagement_score': self._calculate_engagement_score(post),
                'sentiment_keywords': self._extract_sentiment_keywords(post),
                'topic_category': self._categorize_topic(post),
                'viral_potential': self._assess_viral_potential(post)
            }
            headlines_data.append(headline_row)
        
        df = pd.DataFrame(headlines_data)
        
        summary = {
            'total_posts': len(posts),
            'sources_breakdown': df['source'].value_counts().to_dict(),
            'top_topics': df['topic_category'].value_counts().head(5).to_dict(),
            'viral_potential': df['viral_potential'].value_counts().to_dict(),
            'avg_engagement': df['engagement_score'].mean(),
            'top_engaging_posts': df.nlargest(5, 'engagement_score')[['title', 'source', 'engagement_score']].to_dict('records'),
            'sentiment_distribution': self._analyze_sentiment_distribution(df),
            'recommended_headline_angles': self._suggest_headline_angles(df)
        }
        
        return summary
    
    def _analyze_sentiment_distribution(self, df: pd.DataFrame) -> Dict:
        """Analyze sentiment distribution for headline optimization"""
        sentiment_counts = {}
        for keywords in df['sentiment_keywords']:
            if keywords and isinstance(keywords, str):
                for keyword in keywords.split(', '):
                    sentiment_counts[keyword] = sentiment_counts.get(keyword, 0) + 1
        
        return dict(sorted(sentiment_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _suggest_headline_angles(self, df: pd.DataFrame) -> List[str]:
        """Suggest headline angles based on data analysis"""
        angles = []
        
        # High engagement posts
        if len(df) > 0:
            high_engagement = df[df['engagement_score'] > df['engagement_score'].quantile(0.8)]
            if not high_engagement.empty:
                top_topic = high_engagement['topic_category'].mode()
                if not top_topic.empty:
                    angles.append(f"Focus on {top_topic.iloc[0]} content (high engagement)")
        
        # Viral potential
        viral_posts = df[df['viral_potential'] == 'high']
        if not viral_posts.empty:
            angles.append(f"Leverage {len(viral_posts)} high-viral-potential posts")
        
        # Trending topics
        if len(df) > 0:
            trending_topics = df['topic_category'].value_counts().head(3)
            if not trending_topics.empty:
                angles.append(f"Cover trending topics: {', '.join(trending_topics.index)}")
        
        return angles

def create_hive_ready_csv(posts: List[Dict], output_dir: str = "./outputs") -> str:
    """Convenience function to create Hive-ready CSV"""
    hive = HiveIntegration()
    return hive.create_headlines_csv(posts)
