# SpendSense Dashboard Deployment - Complete Guide

## 📋 Overview

This guide covers the deployment of both SpendSense dashboards for demo/presentation purposes:

1. **User Dashboard** (Next.js on Vercel) - Already deployed
2. **Operator Dashboard** (NiceGUI on Railway) - Ready to deploy

## 🚀 Quick Start

**Want to deploy now?** → See [`QUICK_START_DEPLOYMENT.md`](QUICK_START_DEPLOYMENT.md)

**Need detailed instructions?** → Continue reading below

---

## 📚 Documentation Index

| Document | Purpose | Who Should Read |
|----------|---------|-----------------|
| [`QUICK_START_DEPLOYMENT.md`](QUICK_START_DEPLOYMENT.md) | 3-step deployment guide | Everyone - start here |
| [`RAILWAY_OPERATOR_DEPLOY.md`](RAILWAY_OPERATOR_DEPLOY.md) | Complete Railway deployment guide | Detailed deployment steps |
| [`DEPLOY_OPERATOR_COMMANDS.sh`](DEPLOY_OPERATOR_COMMANDS.sh) | Executable deployment script | Run for interactive guidance |
| [`DASHBOARD_ACCESS.md`](DASHBOARD_ACCESS.md) | Access credentials & usage | Stakeholders and demo presenters |
| [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) | What was built and why | Technical overview |

---

## 🎯 Current Status

### ✅ Completed
- [x] Backend API deployed on Railway
- [x] User dashboard deployed on Vercel
- [x] Operator dashboard code production-ready
- [x] Password authentication implemented
- [x] Deployment documentation created

### ⏳ Remaining (Manual Steps)
- [ ] Retrieve Vercel bypass token (2 minutes)
- [ ] Deploy operator dashboard to Railway (5 minutes)
- [ ] Test both dashboards (10 minutes)
- [ ] Share access with stakeholders (2 minutes)

**Total Time Required**: ~20 minutes

---

## 🔐 Security Features

### Operator Dashboard
- ✅ Password-protected login page
- ✅ Session-based authentication
- ✅ Environment-based configuration
- ✅ Secure password storage (SHA256 hash supported)

### User Dashboard
- ⚠️ Protected by Vercel Deployment Protection only
- ⚠️ No application-level auth (by design for MVP demo)

### Backend API
- ⚠️ Public endpoints (no authentication)
- ⚠️ Suitable for demo only, not production

---

## 🛠️ Technical Implementation

### Changes Made

**File**: `ui/app_operator_nicegui.py`

1. **Environment Configuration**:
   - Reads `PORT`, `STORAGE_SECRET`, `RELOAD`, `SHOW` from environment
   - Railway-compatible auto-configuration

2. **Authentication System**:
   - `/login` route with password form
   - Protected main dashboard route
   - Session management
   - Configurable username/password

3. **Production Hardening**:
   - Disabled auto-reload in production
   - Disabled auto-browser open
   - Secure session storage

**New Files**:
- `Procfile.operator` - Railway process definition
- `railway.operator.toml` - Build configuration
- Multiple documentation files (see index above)

---

## 📦 Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│              SpendSense Demo Deployment             │
└─────────────────────────────────────────────────────┘

VERCEL (User Dashboard)
├── URL: https://web-p22ey27iy-ralc.vercel.app
├── Protection: Bypass token required
└── Features: Personas, recommendations, videos

RAILWAY (Backend API)
├── URL: https://prolific-possibility-production.up.railway.app
├── Protection: None (public endpoints)
└── Features: REST API, 25 educational videos

RAILWAY (Operator Dashboard) ⏳ To Deploy
├── URL: TBD (from railway domain command)
├── Protection: Username/password
└── Features: 8 tabs for compliance and oversight
```

---

## 🚦 Deployment Steps (Detailed)

### User Dashboard - Get Access

The user dashboard is already deployed. You just need the bypass token:

1. **Login to Vercel**: https://vercel.com/dashboard
2. **Select Project**: Find and click on the `web` project
3. **Navigate**: Settings → Deployment Protection
4. **Copy Token**: Copy the bypass token
5. **Create URL**: `https://web-p22ey27iy-ralc.vercel.app?x-vercel-set-bypass-cookie=<TOKEN>`
6. **Share**: Send this URL to stakeholders

### Operator Dashboard - Deploy to Railway

1. **Generate Storage Secret**:
   ```bash
   openssl rand -hex 32
   # Save this output
   ```

2. **Set Environment Variables**:
   ```bash
   railway env add OPERATOR_USERNAME=operator
   railway env add OPERATOR_PASSWORD=choose_strong_password
   railway env add STORAGE_SECRET=paste_generated_secret
   railway env add AUTH_ENABLED=true
   railway env add RELOAD=false
   railway env add SHOW=false
   railway env add API_URL=https://prolific-possibility-production.up.railway.app
   ```

3. **Deploy**:
   ```bash
   railway up
   ```

4. **Get URL**:
   ```bash
   railway domain
   ```

5. **Test**:
   - Visit the Railway URL
   - Login with your credentials
   - Verify all 8 tabs work

---

## ✅ Testing Checklist

### User Dashboard
- [ ] Bypass URL allows access
- [ ] Homepage displays welcome
- [ ] Can view user personas
- [ ] Recommendations load
- [ ] Videos play
- [ ] Consent toggle works

### Operator Dashboard
- [ ] Login page displays
- [ ] Credentials work
- [ ] All 8 tabs accessible:
  - [ ] Overview
  - [ ] Users
  - [ ] Signals
  - [ ] Recommendations
  - [ ] Traces
  - [ ] Guardrails
  - [ ] Data Generation
  - [ ] Content Management
- [ ] Can generate test data
- [ ] AI recommendations work (if OpenAI key provided)

### Backend API
- [ ] Health check: `curl https://prolific-possibility-production.up.railway.app/health`
- [ ] Users endpoint: `curl https://prolific-possibility-production.up.railway.app/api/users`
- [ ] Videos endpoint: `curl https://prolific-possibility-production.up.railway.app/api/videos`

---

## 💰 Cost Estimate

**Monthly Costs**:
- Vercel Hobby: $0 (free tier)
- Railway Backend API: ~$3-5
- Railway Operator Dashboard: ~$3-5
- **Total**: ~$5-10/month

**Usage Assumptions**:
- Low demo traffic
- Occasional data generation
- No sustained load

---

## 🆘 Troubleshooting

### Deployment Issues

**Railway build fails**:
```bash
railway logs
# Check for missing dependencies or Python version issues
```

**Environment variables not set**:
```bash
railway env ls
# Verify all required variables are present
```

**Can't access after deployment**:
```bash
railway logs --follow
# Look for startup errors
```

### Authentication Issues

**Operator login fails**:
1. Verify password: `railway env ls | grep OPERATOR_PASSWORD`
2. Try `AUTH_ENABLED=false` temporarily
3. Check browser console for errors

**Vercel bypass doesn't work**:
1. Clear browser cookies
2. Get fresh bypass token
3. Verify URL format is exactly: `?x-vercel-set-bypass-cookie=TOKEN`

### Data Issues

**Operator dashboard shows no data**:
- Operator dashboard currently uses local file access
- Future work: integrate with Railway API
- Workaround: Upload database files to Railway (not recommended)

**User dashboard shows no data**:
- Check backend API: `curl https://prolific-possibility-production.up.railway.app/health`
- Verify CORS is configured
- Check browser network tab

---

## 📞 Support

### Resources
- **Railway Docs**: https://docs.railway.app
- **NiceGUI Docs**: https://nicegui.io
- **Vercel Docs**: https://vercel.com/docs

### Getting Help
- Check deployment logs first
- Review troubleshooting section
- Consult the detailed guides in this repo

---

## 🎓 Demo Workflow

### For Stakeholder Presentations

**1. Start with User Dashboard**:
- Show bypass URL access
- Browse personas (High Utilization, Savings Builder, etc.)
- View personalized recommendations
- Watch educational video
- Toggle consent on/off

**2. Switch to Operator Dashboard**:
- Login as operator
- Show Overview tab (metrics, persona distribution)
- Generate recommendations (try AI mode)
- View decision traces for compliance
- Show Guardrails monitor
- Demonstrate data generation

**3. Show Backend API**:
- Open Swagger docs: `{api_url}/docs`
- Test GET /api/users endpoint
- Show real-time sync with dashboards

**4. Discuss Architecture**:
- Explain fairness metrics
- Show compliance features
- Discuss guardrails and consent management

---

## 🔮 Future Enhancements

### Near-term
- [ ] Integrate operator dashboard with Railway API (no local files)
- [ ] Add user authentication to user dashboard
- [ ] Implement API key auth for backend
- [ ] Add audit logging

### Long-term
- [ ] OAuth/SSO for operator dashboard
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-tenancy support

---

## 📝 Notes

- This is a **demo/MVP deployment**, not production-ready
- Security is basic - suitable for stakeholder presentations only
- For production: implement proper auth, encryption, audit logging
- All synthetic data (no real PII)

---

## 🎉 Summary

You're ready to deploy! Follow these steps:

1. **Quick Path**: [`QUICK_START_DEPLOYMENT.md`](QUICK_START_DEPLOYMENT.md)
2. **Detailed Path**: [`RAILWAY_OPERATOR_DEPLOY.md`](RAILWAY_OPERATOR_DEPLOY.md)
3. **Get Help**: Run `./DEPLOY_OPERATOR_COMMANDS.sh`

**Questions?** Check [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) for technical details.

---

*Last Updated*: November 9, 2025
*Version*: MVP V2 Demo Deployment
*Branch*: feat/production-fairness-metrics
