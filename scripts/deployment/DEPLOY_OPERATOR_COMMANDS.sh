#!/bin/bash

# SpendSense Operator Dashboard - Railway Deployment Commands
# Run these commands manually to deploy the operator dashboard

echo "=== SpendSense Operator Dashboard Deployment ==="
echo ""

# Step 1: Ensure we're in the correct directory
echo "Step 1: Verify working directory"
pwd
echo ""

# Step 2: Check Railway CLI authentication
echo "Step 2: Checking Railway authentication..."
railway whoami
echo ""

# Step 3: Link to Railway project (if not already linked)
echo "Step 3: Linking to Railway project..."
echo "Current status:"
railway status
echo ""
echo "If you need to link to a different project or service, run:"
echo "  railway link"
echo ""

# Step 4: Set environment variables for operator dashboard
echo "Step 4: Setting environment variables..."
echo ""
echo "IMPORTANT: You need to set these variables. Run each command:"
echo ""

# Generate a random storage secret
STORAGE_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "GENERATE_THIS_MANUALLY")

cat << 'EOF'
# Core authentication (REQUIRED)
railway env add OPERATOR_USERNAME=operator
railway env add OPERATOR_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Storage secret for sessions (REQUIRED)
railway env add STORAGE_SECRET=STORAGE_SECRET_HERE

# Production settings
railway env add AUTH_ENABLED=true
railway env add RELOAD=false
railway env add SHOW=false

# Backend API connection
railway env add API_URL=https://prolific-possibility-production.up.railway.app

# Alternative: Use password hash instead of plain password (more secure)
# Generate with: echo -n "your_password" | shasum -a 256
# railway env add OPERATOR_PASSWORD_HASH=your_sha256_hash_here

EOF

echo ""
echo "Generated STORAGE_SECRET for you: $STORAGE_SECRET"
echo "Copy this value and run:"
echo "  railway env add STORAGE_SECRET=$STORAGE_SECRET"
echo ""

# Step 5: Deploy the operator dashboard
echo "Step 5: Deploy to Railway"
echo ""
echo "Run one of these commands:"
echo ""
echo "Option A - Deploy from current directory:"
echo "  railway up"
echo ""
echo "Option B - Deploy specific service (if you created a separate operator service):"
echo "  railway up --service spendsense-operator"
echo ""

# Step 6: Get the public URL
echo "Step 6: Get your deployment URL"
echo "After deployment completes, run:"
echo "  railway domain"
echo ""

# Step 7: Verification
cat << 'EOF'
================================================================================
VERIFICATION CHECKLIST
================================================================================

After deployment:

1. Check deployment logs:
   railway logs

2. Look for successful startup:
   "INFO: Application startup complete"
   "INFO: Uvicorn running on http://0.0.0.0:PORT"

3. Visit your Railway domain URL

4. Test login with credentials:
   Username: operator (or your custom username)
   Password: (the password you set in env vars)

5. Verify all tabs work:
   - Overview
   - Users
   - Signals
   - Recommendations
   - Traces
   - Guardrails
   - Data Generation
   - Content Management

6. Test data generation:
   - Go to Data Generation tab
   - Generate 5 test users
   - Verify it completes successfully

================================================================================
TROUBLESHOOTING
================================================================================

If build fails:
- Check logs: railway logs
- Verify requirements.txt includes all dependencies
- Ensure Python 3.11 is being used

If authentication fails:
- Verify OPERATOR_PASSWORD is set correctly
- Check Railway environment variables
- Try AUTH_ENABLED=false temporarily to debug

If data doesn't load:
- Operator dashboard currently uses local file access
- Consider implementing API integration with backend
- Or upload database to Railway (not recommended)

================================================================================
NEXT STEPS
================================================================================

After successful deployment:

1. Document the access URL and credentials in DASHBOARD_ACCESS.md

2. Test from a different device/browser

3. Share access with stakeholders:
   - URL: [Your Railway domain]
   - Username: operator
   - Password: [Share securely]

4. Monitor logs for any issues:
   railway logs --follow

================================================================================
EOF

echo ""
echo "Deployment guide complete!"
echo "Run the commands above step by step."
echo ""
