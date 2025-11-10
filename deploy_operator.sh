#!/bin/bash

echo "=== Deploying Operator Dashboard to Railway ==="
echo ""

# Set environment variables for the operator service
echo "Setting environment variables..."
railway variables --set "OPERATOR_USERNAME=operator" \
  --set "OPERATOR_PASSWORD=gauntletai" \
  --set "STORAGE_SECRET=9974b932998fdeb6776dbfeac172d169b2e15bf024f9ab96194b28e7e42e0427" \
  --set "AUTH_ENABLED=true" \
  --set "RELOAD=false" \
  --set "SHOW=false" \
  --set "API_URL=https://prolific-possibility-production.up.railway.app"

echo ""
echo "Deploying to Railway..."
railway up

echo ""
echo "Getting deployment URL..."
railway domain

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Access your operator dashboard at the URL above"
echo "Login with:"
echo "  Username: operator"
echo "  Password: gauntletai"
