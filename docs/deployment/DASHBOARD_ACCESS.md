# SpendSense Dashboard Access Guide

## Overview
This document provides access credentials and instructions for both SpendSense dashboards deployed for demo purposes.

---

## User Dashboard (Next.js)

### Deployment Details
- **Platform**: Vercel
- **Current URL**: https://web-p22ey27iy-ralc.vercel.app
- **Status**: Protected by Vercel Deployment Protection

### Accessing the User Dashboard

**Option 1: Vercel Dashboard Method (Recommended)**
1. Log into Vercel at https://vercel.com
2. Navigate to the `web` project
3. Go to Settings → Deployment Protection
4. Copy the bypass token
5. Share URL format: `https://web-p22ey27iy-ralc.vercel.app?x-vercel-set-bypass-cookie=<TOKEN>`

**Option 2: Vercel CLI Method**
```bash
cd web
vercel env pull
# Check .env.local for VERCEL_AUTOMATION_BYPASS_SECRET
```

### Using the Bypass Token
- The bypass token allows temporary access without full account authentication
- Share this URL with stakeholders for demo purposes
- Token is environment-specific (production vs preview)
- Users will only need to access the URL once per browser to set the cookie

### Features Available
- View user financial personas
- Browse personalized recommendations
- Watch educational videos
- Manage consent preferences
- View spending insights

**Note**: No application-level authentication is implemented for MVP demo purposes.

---

## Operator Dashboard (NiceGUI)

### Deployment Details
- **Platform**: Railway
- **URL**: TBD (will be set during deployment)
- **Port**: Auto-assigned by Railway
- **Protection**: HTTP Basic Authentication

### Access Credentials
```
Username: operator
Password: [TO BE SET DURING DEPLOYMENT]
```

### Features Available
1. **Overview Tab**: System health metrics and persona distribution
2. **User Management**: Filter and view user data
3. **Behavioral Signals**: Analysis of spending patterns
4. **Recommendation Review**: Generate and review recommendations (AI or rule-based)
5. **Decision Trace Viewer**: Complete audit trail for compliance
6. **Guardrails Monitor**: Consent management and tone validation
7. **Data Generation**: Generate synthetic test data with persona skewing
8. **Content Management**: Edit educational content and partner offers

### Authentication
The operator dashboard uses HTTP Basic Authentication:
- Username and password required on first access
- Credentials stored in Railway environment variables
- Session persists using NiceGUI's storage system

---

## Backend API

### Deployment Details
- **Platform**: Railway
- **URL**: https://prolific-possibility-production.up.railway.app
- **Status**: Live and operational
- **Authentication**: None (publicly accessible for MVP demo)

### Available Endpoints
- `GET /health` - API health check
- `GET /api/users` - List all users
- `GET /api/users/{user_id}` - Get specific user
- `GET /api/users/{user_id}/recommendations` - Get recommendations
- `GET /api/videos` - List educational videos
- `POST /api/consent/{user_id}` - Update consent
- `GET /api/personas` - Get persona distribution

### Test the API
```bash
# Health check
curl https://prolific-possibility-production.up.railway.app/health

# Get educational videos
curl https://prolific-possibility-production.up.railway.app/api/videos
```

---

## Demo Workflow

### For Stakeholder Presentations

1. **User Dashboard Demo**:
   - Share bypass URL with attendees
   - Show user persona assignment
   - Browse recommendations
   - Watch educational video
   - Toggle consent on/off

2. **Operator Dashboard Demo**:
   - Share operator URL and credentials
   - Show compliance metrics
   - Generate recommendations (try AI mode if OpenAI key available)
   - View decision traces
   - Demonstrate guardrails monitor

3. **API Demo**:
   - Show Swagger docs: `{api_url}/docs`
   - Test endpoints with cURL or Postman
   - Demonstrate real-time data sync between dashboards

---

## Troubleshooting

### User Dashboard Issues
- **Protected screen appears**: Bypass token expired or not set
  - Get new bypass token from Vercel dashboard
  - Clear browser cookies and try again
- **Data not loading**: Check backend API status
  - Verify API is running: `curl https://prolific-possibility-production.up.railway.app/health`

### Operator Dashboard Issues
- **Authentication fails**: Check password
  - Contact admin for credential reset
- **Data generation not working**: Check API connectivity
  - Dashboard connects to Railway API for data operations
- **AI recommendations failing**: Verify OpenAI API key
  - API key must be entered in the AI recommendations section

### Backend API Issues
- **Endpoints return 500 error**: Check Railway logs
  - Railway Dashboard → Project → Deployments → Logs
- **No data returned**: Database may be empty
  - Run data generation from operator dashboard

---

## Security Considerations

### Current MVP Security Posture
- ❌ User dashboard: No authentication (public demo access)
- ✅ Operator dashboard: HTTP Basic Auth (password protected)
- ❌ Backend API: No authentication (public endpoints)

### For Production Deployment
Before production use, implement:
1. **User Dashboard**: Add user authentication (OAuth, Auth0, or similar)
2. **Backend API**: Add API key authentication or JWT tokens
3. **Operator Dashboard**: Upgrade to OAuth or SSO
4. **Data Protection**: Encrypt sensitive data at rest
5. **Audit Logging**: Track all operator actions
6. **HTTPS**: Enforce SSL/TLS (already enabled on Vercel/Railway)

---

## Contact & Support

For access issues or questions:
- **Project Lead**: Casey Manos
- **Repository**: GauntletAI/SpendSense

---

*Last Updated*: [TO BE UPDATED AFTER DEPLOYMENT]
*Version*: MVP V2 Demo Access
