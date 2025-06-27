# Railway.app Deployment Guide

## Step 1: Prepare Your Repository
Make sure all these files are committed to your Git repository:
- `simple_app.py` (main Flask app)
- `wsgi.py` (WSGI entry point)
- `requirements.txt` (Python dependencies)
- `gunicorn.conf.py` (Gunicorn config)
- `railway.json` (Railway config)
- `Procfile` (alternative deployment config)
- `runtime.txt` (Python version)

## Step 2: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "New Project"

## Step 3: Deploy from GitHub
1. Select "Deploy from GitHub repo"
2. Choose your repository
3. Railway will automatically detect it's a Python app
4. Click "Deploy"

## Step 4: Set Environment Variables
1. Go to your project dashboard
2. Click "Variables" tab
3. Add your OpenAI API key:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: `your-actual-api-key-here`
4. Click "Add"

## Step 5: Get Your URL
1. Go to "Settings" tab
2. Copy your custom domain (or use the Railway-provided URL)
3. Your app will be live at: `https://your-app-name.railway.app`

## Step 6: Test Your App
1. Visit your Railway URL
2. Test creating a landing page
3. Test creating a look with hero image generation

## Troubleshooting

### If deployment fails:
1. Check the "Deployments" tab for error logs
2. Make sure all files are committed to Git
3. Verify `requirements.txt` has all dependencies

### If app doesn't start:
1. Check "Logs" tab for startup errors
2. Verify environment variables are set
3. Make sure `wsgi.py` imports the correct app

### Common Issues:
- **Port issues**: Railway automatically sets `PORT` environment variable
- **Missing dependencies**: Check `requirements.txt`
- **API key not set**: Verify `OPENAI_API_KEY` is in Variables

## Updating Your App
1. Make changes locally
2. Commit and push to GitHub
3. Railway automatically redeploys

## Cost
- **Free tier**: $5/month credit (usually enough for small apps)
- **Paid**: Pay-as-you-go after free tier

## Benefits of Railway
- ✅ No server management
- ✅ Automatic HTTPS
- ✅ Git-based deployments
- ✅ Built-in monitoring
- ✅ Easy environment variables
- ✅ Automatic restarts 