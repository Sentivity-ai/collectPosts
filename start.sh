#!/bin/bash

# Social Media Post Collector - Startup Script

echo "🚀 Starting Social Media Post Collector API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$REDDIT_CLIENT_ID" ] || [ -z "$REDDIT_CLIENT_SECRET" ]; then
    echo "⚠️  Warning: Reddit API credentials not set"
    echo "   Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
fi

if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "⚠️  Warning: YouTube API key not set"
    echo "   Set YOUTUBE_API_KEY environment variable"
fi

if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Warning: Hugging Face token not set"
    echo "   Set HF_TOKEN environment variable for upload functionality"
fi

# Start the application
echo "🌐 Starting FastAPI server..."
echo "   API Documentation: http://localhost:8000/docs"
echo "   Alternative Docs:  http://localhost:8000/redoc"
echo "   Health Check:      http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
