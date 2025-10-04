#!/usr/bin/env python3
"""
CollectPosts - Social Media Scraping API
Main entry point for running the FastAPI server
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the FastAPI app
from api.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
