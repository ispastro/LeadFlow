#!/bin/bash

# LeadFlow Heroku Deployment Script
# This script automates the Heroku deployment process

set -e

echo "🚀 LeadFlow Heroku Deployment"
echo "=============================="
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku..."
    heroku login
fi

# Get app name
read -p "Enter your Heroku app name (e.g., leadflow-backend): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name cannot be empty"
    exit 1
fi

# Check if app exists, create if not
if heroku apps:info -a $APP_NAME &> /dev/null; then
    echo "✅ App '$APP_NAME' already exists"
else
    echo "📦 Creating Heroku app '$APP_NAME'..."
    heroku create $APP_NAME
fi

# Set stack to container
echo "🐳 Setting stack to container..."
heroku stack:set container -a $APP_NAME

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
echo "Please provide the following values:"
echo ""

read -p "SUPABASE_DB_URL: " SUPABASE_DB_URL
read -p "GROQ_API_KEY: " GROQ_API_KEY
read -p "QDRANT_URL: " QDRANT_URL
read -p "QDRANT_API_KEY: " QDRANT_API_KEY
read -p "JWT_SECRET (press Enter to generate): " JWT_SECRET

if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT_SECRET: $JWT_SECRET"
fi

heroku config:set \
    SUPABASE_DB_URL="$SUPABASE_DB_URL" \
    GROQ_API_KEY="$GROQ_API_KEY" \
    QDRANT_URL="$QDRANT_URL" \
    QDRANT_API_KEY="$QDRANT_API_KEY" \
    JWT_SECRET="$JWT_SECRET" \
    -a $APP_NAME

echo ""
read -p "Do you want to configure email notifications? (y/n): " SETUP_EMAIL

if [ "$SETUP_EMAIL" = "y" ]; then
    read -p "SMTP_HOST (e.g., smtp.gmail.com): " SMTP_HOST
    read -p "SMTP_PORT (default: 587): " SMTP_PORT
    SMTP_PORT=${SMTP_PORT:-587}
    read -p "SMTP_USER: " SMTP_USER
    read -p "SMTP_PASSWORD: " SMTP_PASSWORD
    read -p "NOTIFICATION_EMAILS (comma-separated): " NOTIFICATION_EMAILS
    
    heroku config:set \
        SMTP_HOST="$SMTP_HOST" \
        SMTP_PORT="$SMTP_PORT" \
        SMTP_USER="$SMTP_USER" \
        SMTP_PASSWORD="$SMTP_PASSWORD" \
        NOTIFICATION_EMAILS="$NOTIFICATION_EMAILS" \
        -a $APP_NAME
fi

# Deploy
echo ""
echo "🚢 Deploying to Heroku..."
cd backend
git init 2>/dev/null || true
heroku git:remote -a $APP_NAME
git add .
git commit -m "Deploy to Heroku" 2>/dev/null || git commit --amend --no-edit
git push heroku main -f

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 View logs: heroku logs --tail -a $APP_NAME"
echo "🌐 Open app: heroku open -a $APP_NAME"
echo "🔍 Check health: curl https://$APP_NAME.herokuapp.com/health"
echo ""
echo "🎉 Your backend is live at: https://$APP_NAME.herokuapp.com"
