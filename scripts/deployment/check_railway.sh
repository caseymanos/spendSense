#!/bin/bash

echo "🚂 Railway Deployment Status Check"
echo "=================================="
echo ""

# Check if we can get Railway project info
echo "📋 Checking Railway projects..."
railway list 2>&1

echo ""
echo "💡 To link this project to Railway:"
echo "   1. Go to Railway dashboard: https://railway.app/dashboard"
echo "   2. Find your SpendSense project"
echo "   3. Check the deployment status"
echo "   4. Look for logs showing:"
echo "      - ✅ Successfully seeded 25 educational videos"
echo "      - ✅ Uvicorn running on http://0.0.0.0:\$PORT"
echo ""
echo "🔗 Or open Railway dashboard automatically:"
echo "   open https://railway.app/dashboard"
