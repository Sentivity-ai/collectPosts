#!/bin/bash

echo "🚀 Force Deploy Script for Render"
echo "=================================="

echo "📝 Current git status:"
git status --porcelain

echo ""
echo "📤 Pushing latest changes..."
git push origin main

echo ""
echo "✅ Changes pushed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Go to your Render dashboard"
echo "2. Find your 'social-media-collector' service"
echo "3. Click 'Manual Deploy' → 'Deploy latest commit'"
echo "4. This will force a clean build with Python 3.11.9"
echo ""
echo "🌐 Your service will be available at: https://your-service-name.onrender.com"
echo ""
echo "📋 If deployment still fails:"
echo "- Check the build logs for Python version"
echo "- Ensure all environment variables are set"
echo "- Contact Render support if Python 3.13 is still being used"
