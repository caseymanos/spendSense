# Quick Deploy Guide

## 🚀 Deploy Backend (5 minutes)

### Option 1: Railway (Easiest)

1. **Go to Railway**
   ```
   https://railway.app
   ```

2. **New Project → Deploy from GitHub**
   - Select `caseymanos/spendSense` repository
   - Railway auto-detects the Dockerfile
   - Click "Deploy"

3. **Get Your Backend URL**
   - Once deployed, Railway provides a public URL like:
   - `https://spendsense-production.up.railway.app`
   - Copy this URL

4. **Test Backend**
   ```bash
   curl https://your-backend-url.railway.app/users
   curl https://your-backend-url.railway.app/videos/hysa
   ```

### Option 2: Render

1. **Go to Render**
   ```
   https://render.com
   ```

2. **New → Web Service**
   - Connect GitHub
   - Select `caseymanos/spendSense`
   - Render detects `render.yaml`
   - Click "Create Web Service"

3. **Get Your Backend URL**
   - Example: `https://spendsense.onrender.com`

## 🎨 Update Frontend (2 minutes)

### Update Vercel Environment Variable

1. **Go to Vercel Dashboard**
   ```
   https://vercel.com/dashboard
   ```

2. **Navigate to SpendSense Project**
   - Go to Settings → Environment Variables

3. **Update API URL**
   - Variable: `NEXT_PUBLIC_API_URL`
   - Value: Your Railway/Render backend URL (from above)
   - Example: `https://spendsense-production.up.railway.app`

4. **Redeploy**
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Click "Redeploy"

## ✅ Verify Deployment

### Backend Endpoints to Test:
```bash
# Replace YOUR_BACKEND_URL with your actual URL

# Health check
curl https://YOUR_BACKEND_URL/users

# Video endpoints (should return real YouTube videos)
curl https://YOUR_BACKEND_URL/videos/hysa
curl https://YOUR_BACKEND_URL/videos/subscription_audit
curl https://YOUR_BACKEND_URL/videos/zero_based_budget
curl https://YOUR_BACKEND_URL/videos/smart_goals
curl https://YOUR_BACKEND_URL/videos/emergency_fund_variable_income

# API documentation
open https://YOUR_BACKEND_URL/docs
```

### Frontend to Test:
1. Open your Vercel URL
2. Click on a user (e.g., user_0006)
3. Scroll to recommendations
4. Click "Watch Video" button
5. Verify YouTube video loads

## 🔧 Troubleshooting

### Backend Not Starting
- Check Railway/Render logs
- Verify all dependencies in `pyproject.toml`
- Ensure database seeding completed

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is publicly accessible
- Test backend endpoints with curl

### Videos Not Loading
- Check backend logs for seed script output
- Test `/videos/{topic}` endpoints directly
- Verify YouTube IDs are valid

## 📊 What Gets Deployed

### Backend Includes:
- ✅ FastAPI REST API
- ✅ SQLite database (auto-seeded)
- ✅ 15 real educational videos across 5 topics
- ✅ All recommendation logic
- ✅ User profiles and personas
- ✅ CORS enabled for frontend

### Frontend Includes:
- ✅ Next.js dashboard
- ✅ User list and profiles
- ✅ Recommendation cards
- ✅ Video dialogs with YouTube embeds
- ✅ Responsive design

## 💰 Cost

- **Railway**: Free tier ($5/month credit) - enough for demo
- **Render**: Free tier available (spins down after inactivity)
- **Vercel**: Free (Hobby tier)

**Total: $0/month for MVP/Demo**

## 🎯 Next Steps

After deployment:
1. Test all functionality
2. Share Vercel URL with stakeholders
3. Monitor Railway/Render for errors
4. Consider adding custom domain
5. Set up monitoring/alerts

## 📚 Full Documentation

See `DEPLOYMENT.md` for:
- Detailed configuration
- Production scaling
- Database migration
- Security considerations
- Custom domain setup
