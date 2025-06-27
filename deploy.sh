#!/bin/bash

# TrendScraper Deployment Script
# This script creates a backup and deploys to Railway

echo "🚀 Starting TrendScraper deployment..."

# Create a backup before deploying
echo "📦 Creating backup before deployment..."
python3 backup_data.py create "pre_deploy_$(date +%Y%m%d_%H%M%S)"

# Add all changes to git
echo "📝 Adding changes to git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Push to Railway
echo "🚀 Pushing to Railway..."
git push origin main

echo "✅ Deployment complete!"
echo "🌐 Your app should be live on Railway in a few minutes"
echo "📦 Backup created in backups/ directory" 