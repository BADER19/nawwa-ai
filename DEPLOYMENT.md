# 🚀 Nawwa Deployment Guide

## Quick Start Deployment

### Prerequisites
- GitHub account
- Accounts on: Supabase, Upstash, Render, Vercel

### 1. Database Setup (Supabase)

1. Go to [supabase.com](https://supabase.com) and create account
2. Click "New Project"
3. Name: `nawwa-db`
4. Generate a strong password
5. Region: Choose closest to you
6. Wait for project to be created
7. Go to Settings → Database
8. Copy the "Connection string" (URI format)
9. Replace `[YOUR-PASSWORD]` with your actual password
10. Save this URL for later

### 2. Redis Setup (Upstash)

1. Go to [upstash.com](https://upstash.com) and create account
2. Click "Create Database"
3. Name: `nawwa-redis`
4. Type: Regional
5. Region: Choose closest to you
6. Click "Create"
7. Copy the "REDIS_URL" from dashboard
8. Save this URL for later

### 3. Push to GitHub

```bash
# Create new repo on GitHub
gh repo create nawwa-ai --public --push --source=.

# Or manually:
# 1. Go to github.com
# 2. Create new repository named "nawwa-ai"
# 3. Run:
git remote add origin https://github.com/YOUR-USERNAME/nawwa-ai.git
git push -u origin master
```

### 4. Deploy Backend (Render)

1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub account if not connected
5. Select `nawwa-ai` repository
6. Configure:
   - **Name:** `nawwa-backend`
   - **Environment:** Docker
   - **Docker Path:** `backend/Dockerfile`
   - **Instance Type:** Free
7. Add Environment Variables (click "Advanced"):
   ```
   DATABASE_URL = [Your Supabase URL]
   REDIS_URL = [Your Upstash URL]
   JWT_SECRET = [Generate random string]
   OPENAI_API_KEY = [Your OpenAI key]
   PAYPAL_MODE = sandbox
   PAYPAL_CLIENT_ID = AarS05gkWVK9IuVh3qyh4ofgZS6x7pFBTb_i38jJAY-MtNklC5vJbNJZD4fNhOkX8FWU4Jz6-Xe8Cc44
   PAYPAL_CLIENT_SECRET = [Your PayPal Secret]
   PAYPAL_PRO_MONTHLY_PLAN_ID = P-38617509FA570261GNEINY2Y
   PAYPAL_PRO_YEARLY_PLAN_ID = P-40539137PY140822CNEIN4VY
   PAYPAL_TEAM_MONTHLY_PLAN_ID = [Add when created]
   PAYPAL_TEAM_YEARLY_PLAN_ID = [Add when created]
   CORS_ORIGINS = https://nawwa.vercel.app
   ```
8. Click "Create Web Service"
9. Wait for deployment (takes ~10 minutes)
10. Copy the URL (like `https://nawwa-backend.onrender.com`)

### 5. Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click "Import Project"
4. Import `nawwa-ai` repository
5. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
6. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_BASE_URL = https://nawwa-backend.onrender.com
   NEXT_PUBLIC_PAYPAL_CLIENT_ID = AarS05gkWVK9IuVh3qyh4ofgZS6x7pFBTb_i38jJAY-MtNklC5vJbNJZD4fNhOkX8FWU4Jz6-Xe8Cc44
   NEXT_PUBLIC_PAYPAL_MODE = sandbox
   ```
7. Click "Deploy"
8. Your app will be live at `https://nawwa.vercel.app`

### 6. Update CORS

After frontend is deployed:
1. Go back to Render dashboard
2. Click on your backend service
3. Go to Environment
4. Update `CORS_ORIGINS` to include your Vercel URL
5. Save and redeploy

## 🎉 Your App is Live!

- Frontend: `https://nawwa.vercel.app`
- Backend: `https://nawwa-backend.onrender.com`
- API Docs: `https://nawwa-backend.onrender.com/docs`

## 📝 Important Notes

1. **Free Tier Limits:**
   - Render backend spins down after 15 min inactivity
   - First request after sleep takes ~30 seconds
   - Supabase: 500MB storage, 2GB bandwidth
   - Upstash: 10,000 Redis commands/day

2. **PayPal Setup:**
   - Complete remaining Team plans in PayPal Dashboard
   - Update plan IDs in Render environment variables
   - Test with sandbox accounts first

3. **Production Checklist:**
   - [ ] Change `PAYPAL_MODE` to `live` when ready
   - [ ] Get production PayPal credentials
   - [ ] Set up custom domain
   - [ ] Enable Render auto-deploy from GitHub
   - [ ] Set up monitoring (Sentry, LogRocket)

## 🔧 Troubleshooting

**Backend not starting?**
- Check Render logs for errors
- Verify all environment variables are set
- Ensure database URL is correct

**Frontend API errors?**
- Check NEXT_PUBLIC_API_BASE_URL is correct
- Verify CORS_ORIGINS includes frontend URL
- Check browser console for errors

**PayPal not working?**
- Verify credentials are correct
- Check PayPal mode (sandbox vs live)
- Ensure plan IDs are valid

## 📧 Support

Need help? Contact: admin@nawwa.ai