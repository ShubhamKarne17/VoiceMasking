# 🚀 Deployment Guide - Voice Privacy Masking System

## 📋 Overview

This project has **two parts** that need to be deployed separately:
- **Frontend (React)**: Deploy to Vercel
- **Backend (Python)**: Deploy to Railway/Render

## 🎯 Deployment Strategy

### Option 1: Vercel + Railway (Recommended)
- Frontend on Vercel (free tier available)
- Backend on Railway (free tier available)

### Option 2: Vercel + Render
- Frontend on Vercel
- Backend on Render (free tier available)

## 📁 What to Push to GitHub

### ✅ Files to Include
```
voice_masking_system/
├── src/
│   ├── backend/           ✅ (Python backend code)
│   └── frontend/          ✅ (React frontend code)
├── requirements.txt       ✅ (Python dependencies)
├── vercel.json           ✅ (Vercel config)
├── railway.json          ✅ (Railway config)
├── Procfile              ✅ (Railway deployment)
├── runtime.txt           ✅ (Python version)
├── .gitignore            ✅ (Updated)
└── README.md             ✅
```

### ❌ Files NOT to Push (already in .gitignore)
- `venv/` (Python virtual environment)
- `node_modules/` (Node.js dependencies)
- `demo_audio/` (Generated audio files)
- `.env` (Environment variables)
- `__pycache__/` (Python cache)
- `dist/` (Build outputs)

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

2. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/voice-masking-system.git
   git push -u origin main
   ```

### Step 2: Deploy Backend to Railway

1. **Go to Railway.app** and sign up/login
2. **Create New Project** → "Deploy from GitHub repo"
3. **Select your repository**
4. **Railway will automatically detect** it's a Python project
5. **Set Environment Variables** (if needed):
   ```
   FLASK_ENV=production
   PORT=5000
   ```
6. **Deploy** - Railway will use the `Procfile` and `requirements.txt`

### Step 3: Get Backend URL

1. **After deployment**, Railway gives you a URL like:
   ```
   https://your-app-name.railway.app
   ```
2. **Test the backend**:
   ```bash
   curl https://your-app-name.railway.app/api/health
   ```

### Step 4: Deploy Frontend to Vercel

1. **Go to Vercel.com** and sign up/login
2. **Create New Project** → "Import Git Repository"
3. **Select your repository**
4. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `src/frontend/voice-masking-ui`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Set Environment Variables**:
   ```
   REACT_APP_API_URL=https://your-app-name.railway.app
   ```

6. **Deploy** - Vercel will build and deploy your frontend

### Step 5: Update Vercel Configuration

After getting your Railway URL, update `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/frontend/voice-masking-ui/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-app-name.railway.app/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/src/frontend/voice-masking-ui/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://your-app-name.railway.app"
  }
}
```

## 🔧 Alternative: Render Deployment

If you prefer Render over Railway:

### Backend on Render

1. **Go to Render.com** and create account
2. **New Web Service** → "Connect a repository"
3. **Select your repository**
4. **Configure**:
   - **Name**: voice-masking-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src/backend && python api_server.py`
   - **Plan**: Free

5. **Set Environment Variables**:
   ```
   FLASK_ENV=production
   PORT=5000
   ```

## 🧪 Testing Your Deployment

### Test Backend
```bash
# Health check
curl https://your-backend-url.railway.app/api/health

# Get profiles
curl https://your-backend-url.railway.app/api/profiles
```

### Test Frontend
1. **Visit your Vercel URL**
2. **Check browser console** for any errors
3. **Test voice processing** (note: real-time audio won't work in browser)

## ⚠️ Important Limitations

### Browser Audio Limitations
- **Real-time audio processing** requires local access to microphone
- **Web browsers** have security restrictions for audio devices
- **The deployed version** will show the UI but **real-time voice masking won't work**

### Why Real-Time Audio Won't Work in Browser
1. **Security**: Browsers block direct microphone access for security
2. **Latency**: Network delay makes real-time processing impossible
3. **Audio APIs**: Web Audio API has limitations compared to desktop

## 🎯 What Works in Deployment

### ✅ What Works
- **Voice profile selection** UI
- **Backend API endpoints**
- **Profile management**
- **Settings configuration**
- **Demo audio generation** (if implemented)

### ❌ What Doesn't Work
- **Real-time voice masking** (requires local desktop app)
- **Live microphone processing**
- **Instant audio transformation**

## 🔄 Continuous Deployment

### Automatic Updates
- **GitHub push** → **Automatic deployment** on both platforms
- **Railway**: Auto-deploys on main branch push
- **Vercel**: Auto-deploys on main branch push

### Manual Updates
```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main
# Both platforms will auto-deploy
```

## 🛠️ Troubleshooting

### Backend Issues
1. **Check Railway logs** for Python errors
2. **Verify requirements.txt** has all dependencies
3. **Check Procfile** syntax
4. **Test locally** first

### Frontend Issues
1. **Check Vercel build logs**
2. **Verify environment variables**
3. **Check API URL** in browser console
4. **Test API endpoints** directly

### Common Errors
- **Module not found**: Check `requirements.txt`
- **Port issues**: Set `PORT` environment variable
- **CORS errors**: Backend needs CORS configuration
- **Build failures**: Check Node.js version compatibility

## 📞 Support

If you encounter issues:
1. **Check platform logs** (Railway/Vercel)
2. **Test locally** first
3. **Verify all files** are pushed to GitHub
4. **Check environment variables**

---

**Remember**: The deployed version is great for showcasing the UI and API, but real-time voice masking requires the desktop application! 🎤➡️🖥️ 