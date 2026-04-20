#!/bin/bash

# LeadFlow Backend Deployment Script (Monorepo)
# Run this from the LeadFlow root directory

set -e

echo "🚀 LeadFlow Backend Deployment (Monorepo)"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: backend/ folder not found"
    echo "   Please run this script from the LeadFlow root directory"
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Install it from:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Logging in to Heroku..."
    heroku login
fi

# Get app name
read -p "Enter your Heroku app name (e.g., leadflow-backend): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name cannot be empty"
    exit 1
fi

# Check if app exists
if heroku apps:info -a $APP_NAME &> /dev/null; then
    echo "✅ App '$APP_NAME' exists"
    read -p "Deploy to existing app? (y/n): " DEPLOY_EXISTING
    if [ "$DEPLOY_EXISTING" != "y" ]; then
        exit 0
    fi
else
    echo "📦 Creating new Heroku app '$APP_NAME'..."
    heroku create $APP_NAME
    
    # Set stack to container
    echo "🐳 Setting stack to container..."
    heroku stack:set container -a $APP_NAME
    
    # Configure environment variables
    echo ""
    echo "⚙️  Let's set up environment variables..."
    read -p "SUPABASE_DB_URL: " SUPABASE_DB_URL
    read -p "GROQ_API_KEY: " GROQ_API_KEY
    read -p "QDRANT_URL: " QDRANT_URL
    read -p "QDRANT_API_KEY: " QDRANT_API_KEY
    
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT_SECRET: $JWT_SECRET"
    
    heroku config:set \
        SUPABASE_DB_URL="$SUPABASE_DB_URL" \
        GROQ_API_KEY="$GROQ_API_KEY" \
        QDRANT_URL="$QDRANT_URL" \
        QDRANT_API_KEY="$QDRANT_API_KEY" \
        JWT_SECRET="$JWT_SECRET" \
        -a $APP_NAME
fi

# Add Heroku remote if not exists
if ! git remote | grep -q "^heroku$"; then
    echo "🔗 Adding Heroku remote..."
    heroku git:remote -a $APP_NAME
else
    echo "✅ Heroku remote already exists"
fi

# Make sure everything is committed
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  You have uncommitted changes. Committing them now..."
    git add .
    git commit -m "Deploy backend to Heroku"
fi

# Deploy using git subtree
echo ""
echo "🚢 Deploying backend folder to Heroku..."
echo "   This may take a few minutes..."
echo ""

git subtree push --prefix backend heroku main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 View logs:    heroku logs --tail -a $APP_NAME"
echo "🌐 Open app:     heroku open -a $APP_NAME"
echo "🔍 Health check: curl https://$APP_NAME.herokuapp.com/health"
echo ""
echo "🎉 Your backend is live at: https://$APP_NAME.herokuapp.com"
