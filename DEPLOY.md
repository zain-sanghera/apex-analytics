# 🚀 Deployment Guide - Apex Analytics

Choose your preferred free hosting platform below:

---

## **Option 1: Render.com** ⭐ (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Apex Analytics"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apex-analytics.git
git push -u origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up (use GitHub)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo

### Step 3: Configure Render
- **Name:** `apex-analytics`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python server.py`
- **Free Tier:** ✅ (one free web service)

### Step 4: Deploy
Click "Create Web Service" and wait ~2-3 minutes. Your app will be live at:
```
https://apex-analytics.onrender.com
```

---

## **Option 2: Railway.app** (Very Beginner-Friendly)

### Step 1: Push to GitHub (same as above)

### Step 2: Connect to Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo

### Step 3: Configure
- Railway auto-detects Python
- Set environment variable: None needed
- Auto-deploys on every push

### Step 4: Get Your URL
It's automatically assigned (e.g., `https://apex-analytics-prod.up.railway.app`)

**Cost:** $5/month free credits (usually lasts months for light usage)

---

## **Option 3: Replit** (Fastest - No GitHub Needed)

### Step 1: Go to https://replit.com

### Step 2: Upload Project
1. Click "New Replit"
2. Choose "Import from GitHub" or upload ZIP
3. Select Python

### Step 3: Click "Run"
- Your app runs instantly
- Public URL auto-generated
- No config needed!

---

## **Local Development**

### Start Server
```bash
cd backupProject
python server.py
```

### Open Browser
```
http://localhost:8000
```

---

## **Troubleshooting**

### "Player not found" error?
- Make sure `data/players.csv` is uploaded
- Check that the server is running

### API calls failing?
- Check browser console (F12) for CORS errors
- Verify the backend URL in server logs

### Port conflicts?
```bash
# Use a different port
PORT=3000 python server.py
```

---

## **Important Notes**

✅ **No external dependencies** - uses only Python built-ins  
✅ **Automatic CORS headers** - works from anywhere  
✅ **Dynamic API URL** - app automatically finds backend  
✅ **Free tier compatible** - works on free hosting plans

---

## **After Deployment**

Your app is now live! Share the URL with your team:
```
https://YOUR_DOMAIN.app
```

Happy analyzing! ⚽
