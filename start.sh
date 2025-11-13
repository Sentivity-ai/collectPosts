#!/bin/bash

echo "🚀 Starting Social Media Collector..."
echo "📊 Python version: $(python --version)"
echo "🌐 Port: $PORT"

# Start the FastAPI application from api directory
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT
