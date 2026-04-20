# Heroku Deployment Guide

This guide will help you deploy the LeadFlow backend to Heroku with CI/CD using GitHub Actions.

## 📋 Prerequisites

- Heroku account (free tier works)
- GitHub account
- Git installed locally
- Heroku CLI installed

## 🚀 Quick Start (Manual Deployment)

### 1. Install Heroku CLI

**Windows:**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or use Chocolatey
choco install heroku-cli
```

**Mac:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login to Heroku

```bash
heroku login
```

### 3. Create Heroku App

```bash
cd backend
heroku create leadflow-backend
# Or use your custom name: heroku create your-app-name
```

### 4. Add PostgreSQL Database (Optional)

```bash
# If you want Heroku Postgres instead of Supabase
heroku addons:create heroku-postgresql:mini
```

### 5. Set Environment Variables

```bash
# Required variables
heroku config:set SUPABASE_DB_URL="postgresql://..."
heroku config:set GROQ_API_KEY="gsk_..."
heroku config:set QDRANT_URL="https://..."
heroku config:set QDRANT_API_KEY="..."
heroku config:set JWT_SECRET="your-secret-key-here"

# Optional email variables
heroku config:set SMTP_HOST="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
heroku config:set SMTP_USER="your-email@gmail.com"
heroku config:set SMTP_PASSWORD="your-app-password"
heroku config:set SMTP_FROM_EMAIL="noreply@leadflow.com"
heroku config:set NOTIFICATION_EMAILS="sales@company.com"

# CORS origins (update after deploying frontend)
heroku config:set ALLOWED_ORIGINS="https://your-dashboard.vercel.app,https://your-widget.vercel.app"

# Admin credentials
heroku config:set ADMIN_EMAIL="admin@leadflow.com"
heroku config:set ADMIN_PASSWORD="admin123"
```

### 6. Deploy to Heroku

**Option A: Using Heroku Git (Buildpack)**
```bash
cd backend
git init
heroku git:remote -a leadflow-backend
git add .
git commit -m "Initial Heroku deployment"
git push heroku main
```

**Option B: Using Docker (Recommended)**
```bash
cd backend
heroku stack:set container
git push heroku main
```

### 7. Check Deployment

```bash
# View logs
heroku logs --tail

# Open app in browser
heroku open

# Check health endpoint
curl https://leadflow-backend.herokuapp.com/health
```

## 🔄 CI/CD Setup (Automated Deployment)

### 1. Get Heroku API Key

```bash
# Login to Heroku
heroku login

# Get your API key
heroku auth:token
```

Copy the token that appears.

### 2. Add GitHub Secrets

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `HEROKU_API_KEY` | Your Heroku API token | `a1b2c3d4-...` |
| `HEROKU_APP_NAME` | Your Heroku app name | `leadflow-backend` |
| `HEROKU_EMAIL` | Your Heroku email | `you@example.com` |

### 3. Push to GitHub

```bash
cd LeadFlow
git add .
git commit -m "Add Heroku deployment config"
git push origin main
```

### 4. Automatic Deployment

Now every time you push to `main` branch with changes in `backend/` folder:
- ✅ GitHub Actions will run
- ✅ Dependencies will be installed
- ✅ Tests will run (if configured)
- ✅ App will deploy to Heroku
- ✅ You'll see deployment status in GitHub Actions tab

### 5. Manual Deployment Trigger

You can also trigger deployment manually:
1. Go to **Actions** tab in GitHub
2. Click **Deploy to Heroku** workflow
3. Click **Run workflow** → **Run workflow**

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
heroku logs --tail

# Last 100 lines
heroku logs -n 100

# Filter by source
heroku logs --source app
```

### Check App Status
```bash
heroku ps
```

### Restart App
```bash
heroku restart
```

### Scale Dynos
```bash
# Check current dynos
heroku ps

# Scale up
heroku ps:scale web=1

# Scale down (stop app)
heroku ps:scale web=0
```

## 🗄️ Database Management

### Connect to Database
```bash
heroku pg:psql
```

### Run Migrations
```bash
heroku run python scripts/setup_database.py
```

### Backup Database
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

## 🔧 Troubleshooting

### App Crashes on Startup

**Check logs:**
```bash
heroku logs --tail
```

**Common issues:**
- Missing environment variables
- Database connection failed
- Port binding issue (make sure using `$PORT`)

### Database Connection Issues

**Check DATABASE_URL:**
```bash
heroku config:get SUPABASE_DB_URL
```

**Test connection:**
```bash
heroku run python -c "import psycopg2; print('Connected!')"
```

### Slow Cold Starts

Heroku free tier sleeps after 30 minutes of inactivity.

**Solutions:**
- Upgrade to Hobby dyno ($7/month, no sleep)
- Use uptime monitoring service (UptimeRobot)
- Accept 10-15 second cold start delay

### Build Failures

**Check build logs:**
```bash
heroku builds
heroku builds:info BUILD_ID
```

**Common fixes:**
- Verify `requirements.txt` is correct
- Check Python version in `runtime.txt`
- Ensure `Procfile` is in root of backend folder

## 📈 Performance Optimization

### Enable HTTP/2
```bash
heroku labs:enable http-session-affinity
```

### Add Redis for Caching (Optional)
```bash
heroku addons:create heroku-redis:mini
```

### Monitor Performance
```bash
heroku addons:create newrelic:wayne
```

## 💰 Cost Breakdown

| Resource | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Web Dyno** | 550 hours/month (sleeps) | $7/month (Hobby, no sleep) |
| **Postgres** | 10k rows, 1GB | $9/month (Mini, 10M rows) |
| **Redis** | 25MB | $3/month (Mini, 100MB) |

**Recommendation:** Start with free tier, upgrade to Hobby dyno ($7/month) when ready for production.

## 🔐 Security Best Practices

### 1. Rotate Secrets Regularly
```bash
heroku config:set JWT_SECRET="new-secret-$(openssl rand -hex 32)"
```

### 2. Enable SSL (Automatic on Heroku)
All `*.herokuapp.com` domains have SSL by default.

### 3. Use Custom Domain (Optional)
```bash
heroku domains:add api.yourdomain.com
# Then add DNS CNAME record pointing to your-app.herokuapp.com
```

### 4. Enable Rate Limiting
Already implemented in FastAPI middleware.

## 🌐 Connect Frontend

After deploying backend, update your frontend:

**Dashboard (.env.production):**
```bash
VITE_API_URL=https://leadflow-backend.herokuapp.com
```

**Widget (.env.production):**
```bash
VITE_API_URL=https://leadflow-backend.herokuapp.com
```

Then update CORS in Heroku:
```bash
heroku config:set ALLOWED_ORIGINS="https://your-dashboard.vercel.app,https://your-widget.vercel.app"
```

## 📞 Support

- **Heroku Docs:** https://devcenter.heroku.com/
- **Heroku Status:** https://status.heroku.com/
- **GitHub Actions Docs:** https://docs.github.com/en/actions

## 🎉 Success Checklist

- [ ] Heroku app created
- [ ] Environment variables set
- [ ] Database connected
- [ ] App deployed successfully
- [ ] Health endpoint returns 200
- [ ] GitHub secrets configured
- [ ] CI/CD pipeline working
- [ ] Frontend connected to backend
- [ ] CORS configured correctly
- [ ] Email notifications working

---

**Your backend is now live at:** `https://your-app-name.herokuapp.com` 🚀
