#!/usr/bin/env python3
"""
CollectPosts Client
Easy access to the API client package
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the client package
from api.client_package import api

# Make the api function available at module level
__all__ = ['api']

if __name__ == "__main__":
    # Example usage
    print("CollectPosts Client - Example Usage:")
    print("from client import api")
    print("data, status = api(subreddit='politics', limit=10)")
    print("print(data.head())")
