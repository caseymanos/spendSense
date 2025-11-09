# Railway Deployment Steps

## 🚀 Deploy SpendSense Backend to Railway

### Method 1: Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   ```
   https://railway.app/dashboard
   ```

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `caseymanos/spendSense` repository
   - Select branch: `feat/production-fairness-metrics`

3. **Configure Service**
   - Railway will auto-detect the `nixpacks.toml` configuration
   - Service Name: `spendsense-api` (or your choice)
   - No additional configuration needed

4. **Deploy**
   - Click "Deploy"
   - Railway will:
     - Install Python 3.11 and uv
     - Run `uv sync` to install dependencies
     - Execute `scripts/seed_educational_videos.py`
     - Start uvicorn server

5. **Get Your URL**
   - Click on your service in Railway
   - Go to "Settings" tab
   - Under "Networking", click "Generate Domain"
   - Copy the public URL (e.g., `https://spendsense-production.up.railway.app`)

### Method 2: Railway CLI (After Manual Setup)

Once you've created the project in the Railway dashboard:

```bash
# Link to your Railway project
railway link

# Check status
railway status

# View logs
railway logs

# Open in browser
railway open
```

## ✅ Verify Deployment

### Check Deployment Logs
In Railway dashboard:
1. Click on your service
2. Go to "Deployments" tab
3. Click on the latest deployment
4. Check logs for:
   - `✅ Successfully seeded 25 educational videos`
   - `Uvicorn running on http://0.0.0.0:$PORT`
   - `Application startup complete`

### Test API Endpoints

Replace `YOUR_RAILWAY_URL` with your actual Railway URL:

```bash
# Health check - should return list of users
curl https://YOUR_RAILWAY_URL/users

# Test video endpoints (should return real YouTube videos)
curl https://YOUR_RAILWAY_URL/videos/hysa | jq '.[0].youtube_id'
curl https://YOUR_RAILWAY_URL/videos/subscription_audit | jq '.[0].title'
curl https://YOUR_RAILWAY_URL/videos/zero_based_budget | jq
curl https://YOUR_RAILWAY_URL/videos/smart_goals | jq
curl https://YOUR_RAILWAY_URL/videos/emergency_fund_variable_income | jq

# View API documentation
open https://YOUR_RAILWAY_URL/docs
```

Expected results:
- `/users` → JSON array of user objects
- `/videos/{topic}` → JSON array of educational videos with YouTube IDs
- `/docs` → Interactive API documentation

## 🔧 Troubleshooting

### Build Fails

**Check logs for:**
- Dependency installation errors
- Python version issues
- Missing files

**Solutions:**
- Ensure `pyproject.toml` and `uv.lock` are committed
- Verify all imports work locally
- Check nixpacks.toml syntax

### Deployment Succeeds but App Crashes

**Check runtime logs for:**
- Database seeding errors
- Import errors
- Port binding issues

**Solutions:**
- Verify `scripts/seed_educational_videos.py` runs without errors locally
- Check that `api.main:app` is the correct module path
- Ensure SQLite database directory (`data/`) is created

### API Returns 404

**Possible causes:**
- Service not started
- Wrong URL
- PORT variable not set

**Solutions:**
- Check Railway logs for startup errors
- Verify the domain is correctly generated
- Ensure `$PORT` environment variable is being used

### Videos Not Loading

**Check:**
- Database seeding in logs
- `/videos/{topic}` endpoint responses
- YouTube video IDs are valid

**Test locally:**
```bash
# Run seed script
uv run python scripts/seed_educational_videos.py

# Check database
sqlite3 data/spendsense.db "SELECT COUNT(*) FROM educational_videos;"
# Should return: 25

# Check specific topic
sqlite3 data/spendsense.db "SELECT youtube_id, title FROM educational_videos WHERE topic='hysa';"
```

## 📊 What to Expect

### Build Time
- First deployment: ~2-3 minutes
- Subsequent deployments: ~1-2 minutes

### Startup Time
- Database seeding: ~5-10 seconds
- API ready: ~10-15 seconds total

### Resource Usage (Free Tier)
- Memory: ~100-200 MB
- CPU: Minimal (REST API is lightweight)
- Disk: ~500 MB (dependencies + database)

## 🎯 Next Steps After Deployment

1. **Copy Your Railway URL**
   - Example: `https://spendsense-production.up.railway.app`

2. **Update Vercel Frontend**
   - Go to Vercel dashboard
   - Project: SpendSense
   - Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your Railway URL
   - Redeploy frontend

3. **Test End-to-End**
   - Open your Vercel frontend
   - Click on a user profile
   - Verify recommendations load
   - Click "Watch Video" button
   - Confirm YouTube video plays

## 💡 Tips

- **Enable auto-deploys**: Railway automatically deploys on git push (already configured)
- **Monitor logs**: Keep logs open during first deployment
- **Test locally first**: Always test changes locally before deploying
- **Use staging**: Consider creating a staging environment for testing

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Railway Status: https://status.railway.app
- Support: https://railway.app/discord
