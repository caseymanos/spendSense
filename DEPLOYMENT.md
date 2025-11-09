# SpendSense Deployment Guide

## Architecture Overview

SpendSense consists of two deployable components:

1. **Frontend**: Next.js application (deployed on Vercel)
2. **Backend**: FastAPI REST API (deployed on Railway/Render)

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub account connected to Vercel
- Repository pushed to GitHub

### Steps

1. **Import Project to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your SpendSense repository
   - Set root directory to `web`

2. **Configure Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

3. **Deploy Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically deploy on every push to your branch

### Update API URL After Backend Deployment
Once your backend is deployed, update the `NEXT_PUBLIC_API_URL` in Vercel:
1. Go to Project Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your Railway/Render backend URL
3. Redeploy the application

## Backend Deployment

You can deploy the FastAPI backend to multiple platforms. Below are instructions for three options:

### Option 1: Railway (Recommended)

1. **Connect Repository**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your SpendSense repository

2. **Configure**
   - Railway will auto-detect the Dockerfile
   - No additional configuration needed
   - Railway automatically provides a public URL

3. **Environment Variables** (Optional)
   - Railway will automatically set `PORT`
   - Add any custom environment variables if needed

4. **Deploy**
   - Railway automatically deploys on push
   - Database seeding happens automatically on startup

### Option 2: Render

1. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your SpendSense repository

2. **Configure**
   - Render will detect `render.yaml`
   - Name: `spendsense-api`
   - Plan: Free (or paid for better performance)

3. **Deploy**
   - Click "Create Web Service"
   - Render automatically builds and deploys

### Option 3: Manual Docker Deployment

If deploying to a custom server:

```bash
# Build the image
docker build -t spendsense-api .

# Run the container
docker run -d -p 8000:8000 --name spendsense spendsense-api

# Check logs
docker logs -f spendsense
```

## Post-Deployment Checklist

### Backend
- [ ] Backend is accessible at public URL
- [ ] `/docs` endpoint shows FastAPI documentation
- [ ] `/users` endpoint returns user list
- [ ] `/videos/hysa` endpoint returns video data
- [ ] Database is seeded with educational videos

### Frontend
- [ ] Frontend loads without errors
- [ ] User list displays correctly
- [ ] User profile pages load
- [ ] Recommendations display with video content
- [ ] Video dialogs open and play YouTube content

### Integration
- [ ] Frontend successfully connects to backend API
- [ ] CORS is properly configured (should be automatic)
- [ ] All API endpoints respond correctly

## Testing Deployments

### Backend Health Check
```bash
# Check API is running
curl https://your-backend-url.railway.app/users

# Check video endpoint
curl https://your-backend-url.railway.app/videos/hysa

# View API docs
open https://your-backend-url.railway.app/docs
```

### Frontend Health Check
1. Visit your Vercel URL
2. Navigate to user profiles
3. Check that recommendations load
4. Test video playback

## Database Considerations

### SQLite in Production
The current setup uses SQLite, which works for MVP/demo purposes but has limitations:

**Pros:**
- Zero configuration
- Embedded with application
- Perfect for demos and MVP

**Cons:**
- Data resets on container restarts (unless using volumes)
- Not suitable for high-traffic production
- No built-in replication

### Data Persistence

**Railway:**
- Add a volume to persist SQLite database
- Go to Service Settings → Volumes
- Mount path: `/app/data`

**Render:**
- Use persistent disk (paid feature)
- Or migrate to PostgreSQL

### Future: Migrate to PostgreSQL
For production scale, consider:
1. Add PostgreSQL service to Railway/Render
2. Update `api/services/` to use SQLAlchemy with PostgreSQL
3. Run migrations to create schema
4. Update connection strings

## Monitoring

### Railway
- Built-in logs and metrics
- Real-time deployment status
- Resource usage graphs

### Render
- Deployment logs in dashboard
- Health checks and uptime monitoring
- Custom metrics available

### Vercel
- Analytics dashboard
- Function logs
- Performance insights

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
- Ensure all dependencies in `pyproject.toml`
- Check that `uv sync` runs successfully
- Verify Dockerfile copies all necessary directories

**Database not seeded:**
- Check startup logs for seed script output
- Verify `scripts/seed_educational_videos.py` runs without errors
- Ensure `data/` directory exists and is writable

**API returns 500 errors:**
- Check application logs
- Verify database file exists and is accessible
- Test endpoints locally first

### Frontend Issues

**"Failed to fetch" errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration in backend (should be `*` for MVP)
- Ensure backend is publicly accessible

**Videos not loading:**
- Check backend `/videos/{topic}` endpoints
- Verify educational videos were seeded
- Test YouTube IDs directly

**Build failures:**
- Check for TypeScript errors
- Verify all dependencies are installed
- Clear `.next` cache and rebuild

## Scaling Considerations

### Current MVP Setup
- Frontend: Serverless (Vercel) - scales automatically
- Backend: Single container - limited scaling

### For Production Scale
1. **Backend:** Multiple instances behind load balancer
2. **Database:** Migrate to PostgreSQL with connection pooling
3. **Caching:** Add Redis for video metadata
4. **CDN:** Use Vercel's CDN for static assets
5. **Monitoring:** Add application performance monitoring (APM)

## Security Notes

- CORS is currently set to `*` (accept all origins) for MVP
- For production: Restrict CORS to specific domains
- Add rate limiting to prevent abuse
- Implement proper authentication if needed
- Use environment variables for sensitive config

## Cost Estimates

### Free Tier (Current)
- Vercel: Free (Hobby plan)
- Railway: $5/month credit (enough for small API)
- Render: Free tier available
- **Total:** $0-5/month

### Paid Tier (For scale)
- Vercel: $20/month (Pro)
- Railway: $20-50/month (more resources)
- PostgreSQL: $7-15/month
- **Total:** $47-85/month

## Support

For deployment issues:
- Railway: [railway.app/help](https://railway.app/help)
- Render: [render.com/docs](https://render.com/docs)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
