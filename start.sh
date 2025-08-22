#!/bin/bash

echo "🚀 Starting Social Media Collector..."
echo "📊 Python version: $(python --version)"
echo "🌐 Port: $PORT"

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port $PORT
