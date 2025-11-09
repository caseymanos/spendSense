# Deploy Operator Dashboard - Run These Commands

## ✅ User Dashboard - DONE!
**URL**: https://spendsense-bli3ypfgf-ralc.vercel.app
**Password**: gauntletai

The user dashboard is now live with password protection!

---

## 🚀 Operator Dashboard - Deploy Now

Run these commands in your terminal:

### Step 1: Set Environment Variables
```bash
railway variables \
  --set "OPERATOR_USERNAME=operator" \
  --set "OPERATOR_PASSWORD=gauntletai" \
  --set "STORAGE_SECRET=9974b932998fdeb6776dbfeac172d169b2e15bf024f9ab96194b28e7e42e0427" \
  --set "AUTH_ENABLED=true" \
  --set "RELOAD=false" \
  --set "SHOW=false" \
  --set "API_URL=https://prolific-possibility-production.up.railway.app"
```

**If no service is linked**, first link/create a service:
```bash
# Option 1: Link to existing service (if you have one)
railway link

# Option 2: Deploy directly (Railway will create service automatically)
railway up
```

### Step 2: Deploy
```bash
railway up
```

### Step 3: Get Your URL
```bash
railway domain
```

---

## 🎯 Access Information

### User Dashboard
- **URL**: https://spendsense-bli3ypfgf-ralc.vercel.app
- **Password**: `gauntletai`
- **Status**: ✅ LIVE

### Operator Dashboard
- **URL**: (will be shown after `railway domain` command)
- **Username**: `operator`
- **Password**: `gauntletai`
- **Status**: ⏳ Ready to deploy (run commands above)

---

## 🔐 Single Password for Everything

Both dashboards use the same password: **`gauntletai`**

- **User Dashboard**: Just enter `gauntletai` when prompted
- **Operator Dashboard**:
  - Username: `operator`
  - Password: `gauntletai`

---

## 🧪 Testing After Deployment

### Test User Dashboard
```bash
# Visit in browser
open https://spendsense-bli3ypfgf-ralc.vercel.app

# Enter password: gauntletai
# Should see dashboard
```

### Test Operator Dashboard
```bash
# Visit in browser (use URL from railway domain command)
open <your-railway-url>

# Login with:
# Username: operator
# Password: gauntletai
```

---

## 📝 Share These Credentials

**For Stakeholders:**
```
SpendSense Demo Access

User Dashboard:
URL: https://spendsense-bli3ypfgf-ralc.vercel.app
Password: gauntletai

Operator Dashboard:
URL: <your-railway-url>
Username: operator
Password: gauntletai
```

---

## ⚡ Quick Commands Reference

```bash
# Deploy operator dashboard
railway up

# Get operator dashboard URL
railway domain

# Check deployment logs
railway logs

# Check deployment status
railway status

# Redeploy if needed
railway up --detach
```

---

## 🆘 Troubleshooting

**"No service linked" error?**
```bash
# Create new service
railway up
# This will automatically create and deploy
```

**Deployment fails?**
```bash
# Check logs
railway logs

# Verify environment variables
railway variables
```

**Can't login?**
```bash
# Check password is set correctly
railway variables | grep OPERATOR_PASSWORD
# Should show: OPERATOR_PASSWORD=gauntletai
```

---

## ✨ Summary

1. **User Dashboard**: Already deployed and working at https://spendsense-bli3ypfgf-ralc.vercel.app
2. **Operator Dashboard**: Just run `railway up` to deploy
3. **Password**: Same for both - `gauntletai`

Total time to complete: **2 minutes** (just one command!)
