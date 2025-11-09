# Quick Start: Deploy Operator Dashboard

## TL;DR - 3 Steps to Deploy

### Step 1: Set Railway Environment Variables (2 minutes)
```bash
# Generate storage secret
openssl rand -hex 32

# Set variables (replace YOUR_PASSWORD and YOUR_SECRET)
railway env add OPERATOR_USERNAME=operator
railway env add OPERATOR_PASSWORD=YOUR_PASSWORD
railway env add STORAGE_SECRET=YOUR_SECRET
railway env add AUTH_ENABLED=true
railway env add RELOAD=false
railway env add SHOW=false
railway env add API_URL=https://prolific-possibility-production.up.railway.app
```

### Step 2: Deploy to Railway (1 command)
```bash
railway up
```

### Step 3: Get Your URL
```bash
railway domain
```

---

## Test Your Deployment

1. Visit the Railway URL from Step 3
2. Login with:
   - Username: `operator`
   - Password: (the password you set in Step 1)
3. Verify all tabs load

---

## Share Access with Stakeholders

### User Dashboard (Already Live)
**URL**: https://web-p22ey27iy-ralc.vercel.app

**To bypass Vercel protection**:
1. Go to https://vercel.com/dashboard
2. Select `web` project → Settings → Deployment Protection
3. Copy bypass token
4. Share: `https://web-p22ey27iy-ralc.vercel.app?x-vercel-set-bypass-cookie=TOKEN`

### Operator Dashboard (After Deployment)
**URL**: (from `railway domain` command)
**Credentials**:
- Username: `operator`
- Password: (share securely)

---

## Need Help?

- **Full Guide**: See `RAILWAY_OPERATOR_DEPLOY.md`
- **Summary**: See `IMPLEMENTATION_SUMMARY.md`
- **Access Docs**: See `DASHBOARD_ACCESS.md`
- **Commands**: Run `./DEPLOY_OPERATOR_COMMANDS.sh` for interactive guide

---

## Troubleshooting

**Railway deployment fails?**
```bash
railway logs
```

**Can't login?**
```bash
railway env ls
# Verify OPERATOR_PASSWORD is set
```

**Need to change password?**
```bash
railway env add OPERATOR_PASSWORD=new_password
# Redeploy will pick up new password automatically
```

---

## That's It!

Total time: ~5-10 minutes
