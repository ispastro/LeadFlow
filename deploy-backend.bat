@echo off
REM LeadFlow Backend Deployment Script (Windows)
REM Run this from the LeadFlow root directory

echo ========================================
echo LeadFlow Backend Deployment (Monorepo)
echo ========================================
echo.

REM Check if backend folder exists
if not exist "backend\" (
    echo Error: backend\ folder not found
    echo Please run this script from the LeadFlow root directory
    pause
    exit /b 1
)

REM Check if Heroku CLI is installed
where heroku >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Heroku CLI not found
    echo Install it from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if logged in
heroku auth:whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Logging in to Heroku...
    heroku login
)

REM Get app name
set /p APP_NAME="Enter your Heroku app name (e.g., leadflow-backend): "

if "%APP_NAME%"=="" (
    echo Error: App name cannot be empty
    pause
    exit /b 1
)

REM Check if app exists
heroku apps:info -a %APP_NAME% >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo App '%APP_NAME%' exists
    set /p DEPLOY_EXISTING="Deploy to existing app? (y/n): "
    if /i not "%DEPLOY_EXISTING%"=="y" exit /b 0
) else (
    echo Creating new Heroku app '%APP_NAME%'...
    heroku create %APP_NAME%
    
    echo Setting stack to container...
    heroku stack:set container -a %APP_NAME%
    
    echo.
    echo Let's set up environment variables...
    set /p SUPABASE_DB_URL="SUPABASE_DB_URL: "
    set /p GROQ_API_KEY="GROQ_API_KEY: "
    set /p QDRANT_URL="QDRANT_URL: "
    set /p QDRANT_API_KEY="QDRANT_API_KEY: "
    
    echo Setting environment variables...
    heroku config:set SUPABASE_DB_URL="%SUPABASE_DB_URL%" -a %APP_NAME%
    heroku config:set GROQ_API_KEY="%GROQ_API_KEY%" -a %APP_NAME%
    heroku config:set QDRANT_URL="%QDRANT_URL%" -a %APP_NAME%
    heroku config:set QDRANT_API_KEY="%QDRANT_API_KEY%" -a %APP_NAME%
    heroku config:set JWT_SECRET="change-this-in-production" -a %APP_NAME%
)

REM Add Heroku remote
git remote | findstr /C:"heroku" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Adding Heroku remote...
    heroku git:remote -a %APP_NAME%
) else (
    echo Heroku remote already exists
)

REM Commit any changes
git diff-index --quiet HEAD
if %ERRORLEVEL% NEQ 0 (
    echo Committing changes...
    git add .
    git commit -m "Deploy backend to Heroku"
)

REM Deploy using git subtree
echo.
echo Deploying backend folder to Heroku...
echo This may take a few minutes...
echo.

git subtree push --prefix backend heroku main

echo.
echo ========================================
echo Deployment complete!
echo ========================================
echo.
echo View logs:    heroku logs --tail -a %APP_NAME%
echo Open app:     heroku open -a %APP_NAME%
echo Health check: curl https://%APP_NAME%.herokuapp.com/health
echo.
echo Your backend is live at: https://%APP_NAME%.herokuapp.com
echo.
pause
