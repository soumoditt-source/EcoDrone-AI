# 🚀 Quick Deployment Guide - EcoDrone AI

## Vercel Deployment (5 Minutes)

### Option 1: Vercel CLI (Fastest)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Navigate to project
cd "C:\Users\Soumoditya Das\Downloads\GEMINI CLOUD IIT"

# 3. Deploy
vercel

# 4. Follow prompts and deploy!
```

### Option 2: GitHub + Vercel (Recommended for Hackathons)

```bash
# 1. Initialize Git (if not already)
git init
git add .
git commit -m "EcoDrone AI - Production Ready"

# 2. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/ecodrone-ai.git
git branch -M main
git push -u origin main

# 3. Go to vercel.com
# - Click "Import Project"
# - Select your GitHub repo
# - Click "Deploy" (Vercel auto-detects config)
```

## Local Testing

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:5173`

## Test with Sample Images

```bash
python generate_samples.py
```

Upload `sample_op1.png` and `sample_op3.png` in the web interface.

## Expected Output
- **Survival Rate**: ~80%
- **Processing Time**: 2-5 seconds
- **Interactive Map**: Green (alive) and red (dead) markers
- **CSV Download**: Available after analysis

## Troubleshooting

**Dependencies not installing?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Frontend build fails?**
```bash
cd frontend
rm -rf node_modules
npm install
npm run build
```

**Vercel deployment fails?**
- Check `vercel.json` is in root directory
- Ensure `frontend/package.json` has `vercel-build` script
- Memory limit: 3008MB (already configured)

---

**You're ready to deploy! 🎉**
