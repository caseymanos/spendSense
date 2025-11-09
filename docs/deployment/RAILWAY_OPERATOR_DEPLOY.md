# Railway Operator Dashboard Deployment Guide

## Prerequisites
- Railway CLI installed (`npm install -g @railway/cli`)
- Railway account with existing project for SpendSense
- Backend API already deployed on Railway

## Deployment Steps

### Option 1: Railway CLI (Recommended)

#### 1. Login to Railway
```bash
railway login
```

#### 2. Link to Project
```bash
# If already in existing project
railway link

# Or select the SpendSense project manually
```

#### 3. Create New Service for Operator Dashboard
```bash
# This will create a new service in your existing Railway project
railway service create spendsense-operator
```

#### 4. Set Environment Variables
```bash
# Required variables
railway variables set OPERATOR_USERNAME=operator
railway variables set OPERATOR_PASSWORD=YOUR_SECURE_PASSWORD_HERE
railway variables set STORAGE_SECRET=$(openssl rand -hex 32)

# Optional variables (defaults shown)
railway variables set AUTH_ENABLED=true
railway variables set RELOAD=false
railway variables set SHOW=false

# Backend API URL (for future API integration)
railway variables set API_URL=https://prolific-possibility-production.up.railway.app
```

**Important**: Replace `YOUR_SECURE_PASSWORD_HERE` with a strong password. This will be used to access the operator dashboard.

#### 5. Deploy
```bash
# Deploy from current directory
railway up

# Or specify the service
railway up --service spendsense-operator
```

#### 6. Get the Public URL
```bash
railway domain
```

This will show you the public URL for your operator dashboard (e.g., `https://spendsense-operator.up.railway.app`).

---

### Option 2: Railway Dashboard (Web UI)

#### 1. Go to Railway Dashboard
Visit https://railway.app/dashboard and select your SpendSense project.

#### 2. Create New Service
- Click "+ New"
- Select "GitHub Repo"
- Choose your `GauntletAI/SpendSense` repository
- Select the `feat/production-fairness-metrics` branch (or main)

#### 3. Configure Service
**Build Settings**:
- Builder: Nixpacks (auto-detected)
- Build Command: (leave empty, Nixpacks handles it)
- Start Command: `python ui/app_operator_nicegui.py`

**Environment Variables** (Settings → Variables):
```
OPERATOR_USERNAME=operator
OPERATOR_PASSWORD=<your-secure-password>
STORAGE_SECRET=<generate-with-openssl-rand-hex-32>
AUTH_ENABLED=true
RELOAD=false
SHOW=false
API_URL=https://prolific-possibility-production.up.railway.app
```

#### 4. Generate Domain
- Go to Settings → Networking
- Click "Generate Domain"
- Note the public URL

#### 5. Deploy
- Click "Deploy" or wait for auto-deploy from GitHub
- Monitor deployment logs in the Deployments tab

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | Auto-assigned by Railway | HTTP port for the dashboard |
| `OPERATOR_USERNAME` | No | `operator` | Login username |
| `OPERATOR_PASSWORD` | **Yes** | None | Plain text password for authentication |
| `OPERATOR_PASSWORD_HASH` | No | None | SHA256 hash of password (alternative to plain) |
| `STORAGE_SECRET` | **Yes** | (insecure default) | Secret key for NiceGUI session storage |
| `AUTH_ENABLED` | No | `true` | Enable/disable authentication |
| `RELOAD` | No | `false` | Hot reload for development (disable in prod) |
| `SHOW` | No | `false` | Auto-open browser (disable in prod) |
| `API_URL` | No | None | Backend API URL for future integration |

### Generating Secure Values

**Storage Secret**:
```bash
openssl rand -hex 32
```

**Password Hash** (alternative to plain password):
```bash
echo -n "your_password" | sha256sum
# Copy the hash and set OPERATOR_PASSWORD_HASH
```

---

## Deployment Verification

### 1. Check Deployment Logs
```bash
railway logs
```

Look for:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:PORT
```

### 2. Test the Dashboard
1. Visit your Railway domain URL
2. Should see login page
3. Login with credentials:
   - Username: `operator` (or your custom username)
   - Password: The password you set in environment variables
4. Verify all tabs load correctly

### 3. Test Data Generation
- Go to "Data Generation" tab
- Try generating a small test dataset (5 users)
- Verify it completes successfully

---

## Connecting to Backend API

The operator dashboard currently uses local file access. To connect it to the Railway backend API:

### Update Required (Future Work):
Modify `ui/utils/data_loaders.py` to:
1. Check for `API_URL` environment variable
2. If set, fetch data from API endpoints instead of local files
3. Implement API client for:
   - `GET /api/users` → load_all_users()
   - `GET /api/signals` → load_all_signals()
   - `GET /api/personas` → load_persona_distribution()

---

## Troubleshooting

### Build Failures

**Error**: `ModuleNotFoundError: No module named 'nicegui'`
- **Solution**: Ensure `nicegui` is in `requirements.txt`
- Check Nixpacks detected Python correctly

**Error**: `ImportError: cannot import name 'ThemeManager'`
- **Solution**: Ensure all local imports are relative and files are in repo
- Check `ui/themes.py` exists

### Runtime Errors

**Error**: Dashboard shows blank page
- **Solution**: Check Railway logs for Python errors
- Verify `PORT` environment variable is being read correctly

**Error**: Login page doesn't accept credentials
- **Solution**: Verify `OPERATOR_PASSWORD` is set correctly
- Check Railway logs for "Invalid credentials" messages
- Try setting `AUTH_ENABLED=false` temporarily to debug

**Error**: Data not loading
- **Solution**: Operator dashboard currently requires local files
- Either:
  - Upload `data/spendsense.db` to Railway (not recommended)
  - Implement API integration (recommended)

### Performance Issues

**Slow startup**:
- Check Nixpacks build cache
- Verify `RELOAD=false` in production

**Memory usage**:
- NiceGUI + Pandas can be memory-intensive
- Consider Railway's memory limits for your plan
- Monitor with `railway status`

---

## Security Considerations

### Authentication
- ✅ Password-protected login page
- ✅ Session-based authentication
- ⚠️ Plain text password in env vars (consider password hash)
- ⚠️ No HTTPS enforcement (Railway provides SSL automatically)

### Best Practices
1. **Use strong passwords**: 16+ characters, mixed case, numbers, symbols
2. **Rotate storage secret**: Change periodically
3. **Monitor access**: Check Railway logs for login attempts
4. **Limit access**: Share credentials only with authorized operators
5. **Enable 2FA**: On your Railway account

### For Production
Before public production use:
- [ ] Implement OAuth/SSO authentication
- [ ] Add audit logging for all operator actions
- [ ] Implement IP whitelisting if needed
- [ ] Add rate limiting on login endpoint
- [ ] Use secrets manager (e.g., Railway Secrets)

---

## Maintenance

### Updating the Dashboard
```bash
# Pull latest changes
git pull origin main

# Railway will auto-deploy if connected to GitHub
# Or manually deploy:
railway up
```

### Viewing Logs
```bash
# Real-time logs
railway logs --follow

# Filter logs
railway logs | grep ERROR
```

### Scaling
Railway auto-scales vertically. For horizontal scaling:
- Consider if multiple operator instances need shared state
- NiceGUI storage is per-instance by default
- May need external session storage (Redis) for multi-instance

---

## Cost Estimation

**Railway Pricing** (as of 2024):
- Hobby Plan: $5/month for 500 execution hours
- Pro Plan: $20/month + usage-based

**Operator Dashboard Usage**:
- Estimated: ~$2-5/month on Hobby plan
- Memory: ~512MB-1GB
- CPU: Low (mostly idle, spikes during data generation)
- Combined with backend API: ~$5-10/month total

---

## Next Steps

After deployment:
1. ✅ Test login and all dashboard features
2. ✅ Document access credentials in `DASHBOARD_ACCESS.md`
3. ⚠️ Implement API integration (currently uses local files)
4. ⚠️ Set up monitoring/alerts for service health
5. ⚠️ Configure backup for any persistent data

---

## Support

- **Railway Docs**: https://docs.railway.app
- **NiceGUI Docs**: https://nicegui.io/documentation
- **Issues**: Contact project admin or check Railway logs
