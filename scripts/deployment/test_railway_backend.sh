#!/bin/bash

# Test Railway Backend Deployment
# Usage: ./test_railway_backend.sh https://your-railway-url.up.railway.app

if [ -z "$1" ]; then
    echo "❌ Please provide your Railway URL"
    echo "Usage: ./test_railway_backend.sh https://your-railway-url.up.railway.app"
    exit 1
fi

RAILWAY_URL="$1"

echo "🚂 Testing Railway Backend: $RAILWAY_URL"
echo "================================================"
echo ""

echo "📋 Test 1: Users endpoint..."
if curl -s -f "$RAILWAY_URL/users" > /dev/null; then
    echo "✅ /users endpoint working"
    USER_COUNT=$(curl -s "$RAILWAY_URL/users" | jq '. | length')
    echo "   Found $USER_COUNT users"
else
    echo "❌ /users endpoint failed"
fi
echo ""

echo "🎬 Test 2: Video endpoints..."
TOPICS=("hysa" "subscription_audit" "zero_based_budget" "smart_goals" "emergency_fund_variable_income")

for topic in "${TOPICS[@]}"; do
    if curl -s -f "$RAILWAY_URL/videos/$topic" > /dev/null; then
        VIDEO_COUNT=$(curl -s "$RAILWAY_URL/videos/$topic" | jq '. | length')
        FIRST_VIDEO=$(curl -s "$RAILWAY_URL/videos/$topic" | jq -r '.[0].youtube_id')
        echo "✅ /videos/$topic: $VIDEO_COUNT videos (first: $FIRST_VIDEO)"
    else
        echo "❌ /videos/$topic failed"
    fi
done
echo ""

echo "📚 Test 3: API Documentation..."
if curl -s -f "$RAILWAY_URL/docs" > /dev/null; then
    echo "✅ /docs endpoint accessible"
else
    echo "❌ /docs endpoint failed"
fi
echo ""

echo "================================================"
echo "🎯 Backend URL for Vercel:"
echo "   $RAILWAY_URL"
echo ""
echo "Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Find SpendSense project → Settings → Environment Variables"
echo "3. Update NEXT_PUBLIC_API_URL to: $RAILWAY_URL"
echo "4. Redeploy the frontend"
