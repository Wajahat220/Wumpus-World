# Step-by-Step Integration & Deployment Guide

Complete guide to integrate React frontend with FastAPI backend and deploy on free platforms.

---

## Part 1: Local Development Setup

### Step 1.1: Prepare Backend

```bash
# Navigate to project
cd wumpus_world_app

# Go to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows (CMD):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Application startup complete.
```

### Step 1.2: Prepare Frontend

```bash
# Open new terminal (keep backend running)

# Navigate to frontend
cd wumpus_world_app/frontend

# Install npm dependencies
npm install

# Start frontend server
npm start
```

You should see:
```
Compiled successfully!
Local: http://localhost:3000
```

### Step 1.3: Test Locally

1. Open browser: `http://localhost:3000`
2. Click "New Game" - grid should appear
3. Click "Auto Move" - agent should move autonomously
4. Verify no console errors

---

## Part 2: Deploy Backend to Railway (Free)

### Step 2.1: Create GitHub Repository

```bash
# Navigate to backend
cd wumpus_world_app/backend

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial FastAPI backend - Wumpus World Agent"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wumpus-world-backend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2.2: Deploy to Railway

1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign Up**: Use GitHub account
3. **Create Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize GitHub if needed
   - Select `wumpus-world-backend` repository

4. **Railway Auto-Detects**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

5. **Wait for Deployment**:
   - Status: "Building..." → "Deployed"
   - Takes ~2-3 minutes

6. **Get Your URL**:
   - Railway provides URL like: `https://wumpus-world-api.railway.app`
   - Note this URL for next step

### Step 2.3: Verify Backend

Test your deployed backend:
```
GET https://YOUR-RAILWAY-URL.railway.app/api/health
```

Should return:
```json
{"status":"healthy","service":"Wumpus World Agent API"}
```

Also check API docs:
```
https://YOUR-RAILWAY-URL.railway.app/docs
```

---

## Part 3: Deploy Frontend to Vercel (Free)

### Step 3.1: Update Configuration

Edit `/workspace/wumpus_world_app/frontend/vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/react-build"
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR-ACTUAL-RAILWAY-URL.railway.app/api/$1"
    }
  ]
}
```

Replace `YOUR-ACTUAL-RAILWAY-URL` with your real Railway URL (without https://).

Edit `/workspace/wumpus_world_app/frontend/.env.production`:
```
REACT_APP_API_URL=https://YOUR-ACTUAL-RAILWAY-URL.railway.app
```

### Step 3.2: Create GitHub Repository

```bash
# Navigate to frontend
cd wumpus_world_app/frontend

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial React frontend - Wumpus World Agent"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wumpus-world-frontend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3.3: Deploy to Vercel

**Option A: Vercel CLI (Recommended)**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend
cd wumpus_world_app/frontend

# Login to Vercel
vercel login
# Follow browser prompts

# Deploy to production
vercel --prod
# Follow prompts:
# - Set up and deploy? Y
# - Which scope? Select your account
# - Project name? wumpus-world-agent
# - Directory? ./
# - Override settings? N

# Get your deployment URL
```

**Option B: Vercel Website**

1. **Go to Vercel**: [vercel.com](https://vercel.com)
2. **Sign Up**: Use GitHub account
3. **Add New Project**:
   - Click "Add New" → "Project"
   - Import `wumpus-world-frontend` repository
   - Framework: "Create React App"
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)

4. **Environment Variables**:
   - Click "Environment Variables"
   - Add: `REACT_APP_API_URL` = Your Railway URL

5. **Deploy**:
   - Click "Deploy"
   - Wait ~2 minutes
   - Get your URL: `https://wumpus-world-frontend.vercel.app`

### Step 3.4: Verify Deployment

1. Open your Vercel URL
2. Click "New Game"
3. Verify grid loads
4. Click "Auto Move" - should work
5. Check browser console for CORS errors (none should appear)

---

## Part 4: Troubleshooting

### CORS Issues

If you get CORS errors:
1. Check backend has CORSMiddleware (it does in our code)
2. Verify vercel.json rewrites are correct
3. Check browser network tab for failed requests

### API Not Connecting

1. Verify Railway backend is running
2. Test directly: `https://YOUR-RAILWAY-URL.railway.app/api/health`
3. Update .env.production with correct URL
4. Redeploy frontend

### Build Failures

For React build errors:
```bash
cd frontend
npm run build
# Check for errors
npm audit fix
npm install
npm run build
```

For Python build errors:
```bash
cd backend
pip install -r requirements.txt
python app.py
# Check for import errors
```

---

## Part 5: Final Checklist

| Task | Status |
|------|--------|
| Backend runs locally | ☐ |
| Frontend runs locally | ☐ |
| Backend deployed to Railway | ☐ |
| Backend API tested | ☐ |
| Frontend configured for production | ☐ |
| Frontend deployed to Vercel | ☐ |
| Full functionality tested | ☐ |

---

## URLs Format After Deployment

| Service | Platform | URL Format |
|---------|----------|------------|
| Frontend | Vercel | `https://wumpus-world-frontend.vercel.app` |
| Backend API | Railway | `https://wumpus-world-api.railway.app` |
| API Docs | Railway | `https://wumpus-world-api.railway.app/docs` |

---

## Alternative: If Railway Expires

Railway free tier expires after 30 days of inactivity. Alternatives:

### Render.com (Free)
1. Create account at render.com
2. "New" → "Web Service"
3. Connect GitHub
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Set PORT environment variable

### PythonAnywhere (Free Tier)
1. Create account at pythonanywhere.com
2. Upload app.py and requirements.txt
3. Open Bash console
4. `pip install -r requirements.txt`
5. Run: `python app.py`
6. Note: Only works while console is open

### Cyclic.sh (Free)
1. Connect GitHub
2. Auto-deploys Node.js (not Python)
3. Not suitable for FastAPI

---

## Summary

### Backend Files
```
/workspace/wumpus_world_app/backend/
├── app.py              # FastAPI application with Resolution engine
├── requirements.txt     # Python dependencies
└── Procfile           # Railway deployment config
```

### Frontend Files
```
/workspace/wumpus_world_app/frontend/
├── public/
│   └── index.html     # HTML template
├── src/
│   ├── App.js        # Main React component
│   ├── App.css       # Styles
│   ├── index.js      # Entry point
│   └── index.css     # Global styles
├── package.json      # Node dependencies
├── vercel.json       # Vercel rewrites config
├── .env             # Local environment
└── .env.production   # Production environment
```

### Integration Steps
1. Run `python app.py` in backend folder
2. Run `npm start` in frontend folder
3. Frontend connects to backend at `http://localhost:5000`
4. Deploy backend to Railway
5. Update frontend with Railway URL
6. Deploy frontend to Vercel
7. Done! Your app is live.

