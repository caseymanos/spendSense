# SpendSense Cloud Deployment Plan

## ✅ Just Completed
- Merged `feat/production-fairness-metrics` into `main`
- All latest features now in main branch
- Repository is production-ready

---

## Current Deployment Status

### What's Already Live

1. **Backend API** ✅
   - **Platform**: Railway
   - **URL**: https://prolific-possibility-production.up.railway.app
   - **Status**: Live and working
   - **Features**: All API endpoints, 25 educational videos seeded
   - **Worktree**: `/Users/caseymanos/GauntletAI/spendsense-persona-test` (main branch)

2. **User Dashboard (Old)** ✅
   - **Platform**: Vercel
   - **URL**: https://spendsense.vercel.app
   - **Status**: Live (Chakra UI version, no password)
   - **Note**: This is an older version

### What's Local Only

1. **Operator Dashboard** ⏳
   - **File**: `ui/app_operator_nicegui.py`
   - **Port**: 8085 (local)
   - **Status**: Production-ready code, not deployed
   - **Features**: Password auth implemented, 8 functional tabs

2. **User Dashboard (New)** ⏳
   - **Directory**: `web/` (Next.js)
   - **Status**: Has password gate code, deployment issues
   - **Note**: Different from live Chakra version

---

## Deployment Plan: Get Everything Cloud-Hosted

### Step 1: Deploy Operator Dashboard to Railway (Priority 1)

**Why Railway**: Already hosting the backend API successfully

**Commands**:
```bash
cd /Users/caseymanos/GauntletAI/SpendSense

# Link to Railway project (will prompt for service selection)
railway link

# Create a new service for operator dashboard or select existing
# When prompted, choose "Create new service" → name it "spendsense-operator"

# Set environment variables
railway variables --set "OPERATOR_USERNAME=operator" \
  --set "OPERATOR_PASSWORD=gauntletai" \
  --set "STORAGE_SECRET=9974b932998fdeb6776dbfeac172d169b2e15bf024f9ab96194b28e7e42e0427" \
  --set "AUTH_ENABLED=true" \
  --set "RELOAD=false" \
  --set "SHOW=false" \
  --set "API_URL=https://prolific-possibility-production.up.railway.app"

# Deploy
railway up

# Get the public URL
railway domain
```

**Expected Result**: Operator dashboard live at `https://spendsense-operator-XXXXX.up.railway.app`

**Login**:
- Username: `operator`
- Password: `gauntletai`

---

### Step 2: Fix & Deploy Next.js User Dashboard to Vercel (Priority 2)

**Current Issue**: The `web/` Next.js app has deployment/routing issues

**Option A: Quick Fix - Use Existing Working Dashboard**
The old Chakra UI dashboard at https://spendsense.vercel.app is already working. Keep using it for now.

**Option B: Fix Next.js Dashboard**
If you want the new Next.js dashboard with password protection:

1. **Identify the issue**:
   ```bash
   cd /Users/caseymanos/GauntletAI/SpendSense/web

   # Check which Vercel project it's linked to
   cat .vercel/project.json

   # Try deploying fresh
   vercel --prod
   ```

2. **Possible fixes**:
   - Remove the PasswordGate component (causing client-side issues)
   - Use Vercel's built-in password protection instead
   - Or keep the old Chakra dashboard live (it works!)

**Recommendation**: Keep using https://spendsense.vercel.app for user dashboard (it's already working)

---

### Step 3: Ensure Backend API is Using Latest Code (Priority 3)

**Current Backend Location**: `/Users/caseymanos/GauntletAI/spendsense-persona-test` (main branch worktree)

**Update Backend**:
```bash
cd /Users/caseymanos/GauntletAI/spendsense-persona-test

# Pull latest main (which now has all your changes)
git pull origin main

# Trigger Railway redeploy
# Railway should auto-deploy on git push, or manually:
railway up --service <backend-service-name>
```

**Verify**:
```bash
curl https://prolific-possibility-production.up.railway.app/health
curl https://prolific-possibility-production.up.railway.app/api/videos | jq length
```

---

## Architecture After Full Deployment

```
┌─────────────────────────────────────────────────────────┐
│              CLOUD ARCHITECTURE                          │
└─────────────────────────────────────────────────────────┘

Internet
   │
   ├──────────────┬────────────────┬──────────────────────┐
   │              │                │                      │
   ▼              ▼                ▼                      ▼
┌──────────┐  ┌──────────┐  ┌───────────────┐  ┌─────────────┐
│ Vercel   │  │ Railway  │  │   Railway     │  │   Users     │
│          │  │          │  │               │  │(Stakeholders│
│User      │◄─►│ Backend  │◄─►│  Operator     │◄─►│  Admins)    │
│Dashboard │  │   API    │  │  Dashboard    │  │             │
└──────────┘  └──────────┘  └───────────────┘  └─────────────┘
     │             │                 │
Chakra UI    FastAPI +         NiceGUI +
 (Public)     SQLite        Password Auth
              Parquet
```

---

## Cost Breakdown (Estimated Monthly)

**Railway** (~$10-15/month):
- Backend API: ~$5-7
- Operator Dashboard: ~$5-8
- Total execution hours well within Hobby plan limits

**Vercel** ($0):
- User dashboard within free tier (low traffic demo)

**Total**: ~$10-15/month for full cloud deployment

---

## Deployment Checklist

- [ ] **Step 1**: Deploy operator dashboard to Railway
  - [ ] Run `railway link` and create/select service
  - [ ] Set environment variables
  - [ ] Run `railway up`
  - [ ] Get public URL with `railway domain`
  - [ ] Test login (operator/gauntletai)

- [ ] **Step 2**: Verify backend API is current
  - [ ] Update spendsense-persona-test worktree to latest main
  - [ ] Confirm Railway auto-deployed
  - [ ] Test API endpoints

- [ ] **Step 3**: User dashboard decision
  - [ ] Keep using https://spendsense.vercel.app (working now)
  - [ ] OR fix Next.js version later

- [ ] **Step 4**: Documentation
  - [ ] Update ACCESS.md with all live URLs
  - [ ] Share credentials with stakeholders

---

## Quick Commands Reference

```bash
# Check what Railway is currently deploying
cd /Users/caseymanos/GauntletAI/spendsense-persona-test
git log -1 --oneline

# Update backend to latest
cd /Users/caseymanos/GauntletAI/spendsense-persona-test
git pull origin main

# Deploy operator dashboard
cd /Users/caseymanos/GauntletAI/SpendSense
railway link  # Select/create operator service
railway variables --set "OPERATOR_USERNAME=operator" --set "OPERATOR_PASSWORD=gauntletai" --set "STORAGE_SECRET=9974b932998fdeb6776dbfeac172d169b2e15bf024f9ab96194b28e7e42e0427" --set "AUTH_ENABLED=true" --set "RELOAD=false" --set "SHOW=false" --set "API_URL=https://prolific-possibility-production.up.railway.app"
railway up
railway domain

# Test deployments
curl https://prolific-possibility-production.up.railway.app/health
open https://spendsense.vercel.app
```

---

## Success Criteria

✅ **Backend API**: Live on Railway, all endpoints working
✅ **User Dashboard**: Live on Vercel (Chakra UI version)
⏳ **Operator Dashboard**: Deploy to Railway (ready to go)

**Timeline**: 10-15 minutes to get operator dashboard live

---

## Next Steps

1. **Now**: Deploy operator dashboard (commands above)
2. **Soon**: Test all three services together
3. **Later**: Consider migrating to Next.js user dashboard (optional)

Everything is production-ready and pushed to main. Just need to run the Railway deployment commands! 🚀
