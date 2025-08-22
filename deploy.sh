#!/bin/bash

echo "🚀 Preparing for Render deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote origin found. Please add your GitHub repository:"
    echo "   git remote add origin https://github.com/yourusername/yourrepo.git"
    exit 1
fi

# Check if all files are committed
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Uncommitted changes found. Please commit your changes:"
    echo "   git add ."
    echo "   git commit -m 'Update for deployment'"
    exit 1
fi

echo "✅ Repository is ready for deployment"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Code pushed to GitHub!"
echo ""
echo "📋 Next steps for Render deployment:"
echo "1. Go to https://dashboard.render.com/"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Render will auto-detect render.yaml configuration"
echo "5. Set your environment variables:"
echo "   - REDDIT_CLIENT_ID"
echo "   - REDDIT_CLIENT_SECRET"
echo "   - YOUTUBE_API_KEY"
echo "   - HF_TOKEN"
echo "   - INSTAGRAM_USERNAME (optional)"
echo "   - INSTAGRAM_PASSWORD (optional)"
echo ""
echo "🌐 Your service will be available at: https://your-service-name.onrender.com"
