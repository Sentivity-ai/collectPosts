#!/bin/bash

echo "🚀 Starting Social Media Collector..."
echo "📊 Python version: $(python --version)"
echo "🌐 Port: $PORT"

# Start the FastAPI application from api directory
# Use --timeout-keep-alive to prevent premature timeouts
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 30
