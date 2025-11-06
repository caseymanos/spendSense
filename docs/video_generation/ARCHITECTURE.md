# SORA Video Generation - System Architecture

**Project:** SpendSense MVP V2 - Video Enhancement
**Timeline:** 6 weeks (3 chunks)
**Last Updated:** 2025-01-05

---

## Executive Summary

This document describes the complete architecture for integrating OpenAI SORA video generation into SpendSense's recommendation system. The system generates personalized 5-10 second educational videos for financial recommendations, with comprehensive fallback strategies, cost controls, and quality governance.

### Key Metrics
- **Total Implementation:** 6 weeks, 3 chunks
- **Total Code:** ~7,117 lines (35 new files, 22 modified files)
- **Expected Cost:** $72-150/month (with 75%+ cache hit rate)
- **Performance Target:** <2s video load, >70% completion rate, <500ms page impact

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SORA VIDEO GENERATION SYSTEM                     │
│                                                                       │
│  User Request → Persona Assignment → Video Job Queue → SORA API      │
│                                           ↓                           │
│                                    Cache Layer (Redis + Disk)        │
│                                           ↓                           │
│                              Fallback: SORA → Infographic → Text     │
│                                           ↓                           │
│                                  Frontend VideoPlayer                │
│                                           ↓                           │
│                              Analytics & Cost Tracking               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - REST API endpoints
- **Redis** - Job queue + metadata cache
- **RQ (Redis Queue)** - Background job processing
- **SQLite** - Relational data
- **Parquet** - Analytics storage
- **OpenAI SORA API** - Video generation

### Frontend
- **Next.js 14.2** - React framework (App Router)
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - Component library
- **TanStack Query** - Data fetching + caching

### Infrastructure
- **uv** - Python environment manager
- **ffmpeg** - Video validation + thumbnail generation
- **Pillow** - Infographic generation (fallback)

---

## Component Architecture

### 1. Video Generation Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                    VIDEO GENERATION FLOW                          │
└──────────────────────────────────────────────────────────────────┘

1. Persona Assignment (personas/assignment.py)
   ↓
   For each top-3 recommendation:

2. Check Cache (recommend/video_cache.py)
   ├─ Cache HIT → Return URL (done)
   └─ Cache MISS → Continue

3. Check Budget (api/services/cost_management.py)
   ├─ Over budget → Generate infographic fallback
   └─ Within budget → Continue

4. Enqueue Job (recommend/video_enqueue.py)
   ↓
   Redis Queue: {persona, topic, cache_key, priority}

5. RQ Worker (recommend/video_worker.py)
   ├─ Build prompt from template (recommend/video_templates.py)
   ├─ Call SORA API (30s timeout, 3 retries)
   ├─ Fallback chain: SORA → Static → Text
   ├─ Validate video (recommend/video_validator.py)
   ├─ Generate thumbnail (recommend/thumbnail_generator.py)
   ├─ Save to disk: data/videos/{persona}/{topic}/{hash}.mp4
   └─ Update cache + trace JSON

6. Frontend Fetch (web/components/VideoPlayer.tsx)
   ├─ Lazy load on viewport intersection
   ├─ Track analytics (play, progress, complete)
   └─ Graceful fallback on error
```

### 2. Cache Architecture

**Storage Layers:**
- **Redis:** Metadata + status (fast lookups, built-in TTL)
- **Filesystem:** Video files (cheap, handles large files)

**Cache Key Design:**
```python
cache_key = sha256(f"{persona}:{topic}")[:16]
# Example: sha256("high_utilization:credit_utilization") → "a3f2b8c9d1e4f7a2"
```

**Why NOT user-specific?**
- Maximizes cache hits (100 users × 3 recs = only 20 unique videos needed)
- Educational content is generic (not personalized to individual user data)
- Target cache hit rate: 75-85% in steady state

**TTL Policy:**
- Videos: 30 days (configurable)
- Processing status: 1 hour
- Failed status: 24 hours

**Eviction Policy:**
- Trigger: Disk usage > 5GB
- Strategy: LRU (least recently used)
- Safety: Don't delete files modified in last 24 hours

### 3. Fallback Strategy

**Decision Tree:**
```
1. Video URL exists && status == 'ready'
   → Serve SORA video ✅

2. Video URL exists && status == 'loading'
   → Show skeleton loader with ETA ⏳

3. Video URL == null || status == 'failed'
   → Check infographic_url

4. Infographic URL exists
   → Serve static SVG/PNG infographic 📊

5. No media available
   → Text-only recommendation (existing implementation) 📝
```

**Fallback Sources:**
- **SORA API:** Primary (best quality, dynamic animation)
- **Static Infographic:** SVG templates with data overlays (fast, lightweight)
- **Text-only:** Existing recommendation cards (100% reliable)

### 4. Cost Management

**Budget Controls:**
```python
DAILY_BUDGET = 5.00  # $150/month ÷ 30 days
SORA_COST_PER_VIDEO = 0.05  # Estimated (subject to SORA pricing)
```

**Enforcement Points:**
1. **Pre-generation check:** `cost_tracker.can_afford_video()` before enqueueing
2. **Daily tracking:** `data/video_costs.json` logs all generation events
3. **Operator override:** Approval queue for over-budget videos
4. **Alerts:** Email at 80% budget, hard cap at 120%

**Expected Costs:**
- Initial generation: 20 unique videos × $0.05 = $1.00
- Monthly regeneration (cache misses): ~50 videos × $0.05 = $2.50
- **Total:** ~$3.50/month (well under $150 budget)

---

## Data Flow Diagrams

### End-to-End User Request Flow

```
┌─────────────┐
│ User visits │
│ dashboard   │
└──────┬──────┘
       │
       v
┌────────────────────────────┐
│ GET /recommendations       │
│ (web/app/dashboard)        │
└──────┬─────────────────────┘
       │
       v
┌────────────────────────────┐
│ generate_recommendations() │
│ (recommend/engine.py)      │
├────────────────────────────┤
│ 1. Load user context       │
│ 2. Detect signals          │
│ 3. Assign persona          │
│ 4. Select education items  │
│ 5. Check video cache       │
│ 6. Add video_url if ready  │
└──────┬─────────────────────┘
       │
       v
┌────────────────────────────┐
│ Return JSON response       │
├────────────────────────────┤
│ {                          │
│   "recommendations": [     │
│     {                      │
│       "title": "...",      │
│       "video_url": "...",  │ ← May be null/loading
│       "video_status": "ready"│
│     }                      │
│   ]                        │
│ }                          │
└──────┬─────────────────────┘
       │
       v
┌────────────────────────────┐
│ Frontend renders           │
│ (RecommendationCard.tsx)   │
├────────────────────────────┤
│ If video_url exists:       │
│   → Show VideoPlayer       │
│ Else if infographic:       │
│   → Show static image      │
│ Else:                      │
│   → Text-only card         │
└────────────────────────────┘
```

### Background Video Generation Flow

```
┌─────────────────────────────┐
│ Persona Assignment Complete │
│ (personas/assignment.py)    │
└──────┬──────────────────────┘
       │
       │ For each user's top 3 recommendations:
       v
┌─────────────────────────────┐
│ enqueue_video_generation()  │
│ (recommend/video_enqueue.py)│
├─────────────────────────────┤
│ 1. Check cache              │
│    ├─ Hit → Return "cached" │
│    └─ Miss → Continue       │
│ 2. Check budget             │
│    └─ Over → Return "skipped"│
│ 3. Enqueue RQ job           │
└──────┬──────────────────────┘
       │
       v
┌─────────────────────────────┐
│ Redis Queue                 │
│ Job: {persona, topic, id}   │
└──────┬──────────────────────┘
       │
       v
┌─────────────────────────────┐
│ RQ Worker Process           │
│ (recommend/video_worker.py) │
├─────────────────────────────┤
│ 1. Dequeue job              │
│ 2. Check cache (idempotency)│
│ 3. Get template             │
│ 4. Call SORA API            │
│    ├─ Success → Continue    │
│    ├─ Timeout → Retry (3x)  │
│    └─ Fail → Fallback       │
│ 5. Validate video           │
│ 6. Generate thumbnail       │
│ 7. Save to disk             │
│ 8. Update cache             │
└──────┬──────────────────────┘
       │
       v
┌─────────────────────────────┐
│ Cache Updated               │
│ (Redis + trace JSON)        │
├─────────────────────────────┤
│ video:{cache_key} = {       │
│   status: "ready",          │
│   url: "/videos/...",       │
│   hash: "abc123",           │
│   created_at: "2025-01-05"  │
│ }                           │
└─────────────────────────────┘
```

---

## File Organization

### New Directories
```
docs/video_generation/          # This documentation
data/videos/                    # Video storage (gitignored)
  ├── high_utilization/
  │   ├── credit_utilization/
  │   │   └── {hash}.mp4
  │   └── debt_paydown_strategy/
  ├── variable_income/
  ├── subscription_heavy/
  └── savings_builder/
data/thumbnails/                # Video thumbnails (gitignored)
data/video_costs.json          # Cost tracking
recommend/templates/            # SVG infographic templates
tests/mocks/                    # Mock SORA client
```

### Key Files by Chunk

**Chunk 1 (POC):**
- `recommend/video_generator.py` - SORA API client
- `recommend/prompt_templates.py` - Template system
- `tests/mocks/sora_mock.py` - Mock for testing

**Chunk 2 (Scale-out):**
- `recommend/video_cache.py` - Cache management
- `recommend/video_worker.py` - RQ worker
- `recommend/video_enqueue.py` - Job queueing
- `recommend/video_cleanup.py` - Cache cleanup
- `api/main.py` - Video API endpoints

**Chunk 3 (UX + Ops):**
- `web/components/VideoPlayer.tsx` - Video player component
- `web/lib/analytics.ts` - Event tracking
- `recommend/infographic_generator.py` - SVG fallbacks
- `recommend/video_validator.py` - Quality checks
- `api/services/cost_management.py` - Budget controls
- `api/services/ab_testing.py` - A/B testing
- `ui/app_operator_nicegui.py` - Operator dashboard (enhanced)

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cache hit rate | >75% | Redis cache GET/SET ratio |
| Video generation time | <30s | SORA API response time |
| Video load time (cached) | <2s | Time to first frame |
| Page load impact | <500ms | Lighthouse FCP delta |
| Video quality | 720p+ | ffprobe validation |
| API uptime | >99% | Health check monitoring |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Monthly cost | <$150 | cost_management.py tracking |
| Video completion rate | >70% | Analytics (complete/play events) |
| User engagement lift | +20% | A/B test (video vs control) |
| Operator approval time | <5 min/video | Operator dashboard metrics |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Validation pass rate | >95% | video_validator.py results |
| Fallback usage | <10% | Infographic served / total |
| Error rate | <5% | Failed video generations |
| Mobile playback | 100% | iOS/Android test matrix |

---

## Security & Privacy

### Data Protection
- **No PII in video URLs:** Use opaque recommendation IDs, not user IDs
- **Local storage:** All videos stored on same machine as database
- **Consent enforcement:** Video generation blocked if user revoked consent
- **Audit trail:** All decisions logged to trace JSONs

### API Security
- **SORA API key:** Stored in environment variable (`.env`, not in code)
- **Rate limiting:** Redis-based rate limiter on API endpoints
- **CORS:** Restricted to frontend domain
- **Authentication:** Inherit from existing recommendation API

### Content Policy
- **Manual review:** Operator approval queue for first-time templates
- **Prohibited language:** Tone validator blocks shaming words
- **Accessibility:** All videos include text alternatives (rationale field)

---

## Scalability Considerations

### Current Capacity (MVP)
- **Users:** 100 (synthetic dataset)
- **Unique videos:** 20 (4 personas × 5 topics)
- **Cache size:** ~1GB (20 videos × ~50MB each)
- **Worker concurrency:** 1 worker (sufficient for POC)

### Growth Path (Post-MVP)
- **1,000 users:** Same 20 videos (cache hit rate → 95%)
- **10,000 users:** Add CDN for video delivery
- **100,000 users:** Horizontal scaling of RQ workers
- **Custom personas:** Expand to 10 personas → 50 unique videos

### Bottlenecks & Mitigation
1. **SORA API rate limits:**
   - Mitigation: Aggressive caching, batch generation during off-peak
2. **Disk I/O for video serving:**
   - Mitigation: Add CDN (CloudFlare, AWS CloudFront)
3. **Redis memory for cache metadata:**
   - Mitigation: Redis cluster, TTL-based eviction
4. **Worker queue backlog:**
   - Mitigation: Multiple worker processes, priority queues

---

## Monitoring & Observability

### Logs
- **Application logs:** Python `logging` module (INFO/WARNING/ERROR)
- **Video generation:** Structured logs with job_id, persona, topic, duration
- **Cost tracking:** Daily summary in `data/video_costs.json`
- **Analytics:** Video events appended to `docs/traces/{user_id}.json`

### Metrics (Future)
- **Prometheus:** Video generation latency, cache hit rate, cost per day
- **Grafana:** Dashboards for operator monitoring
- **Alerts:** PagerDuty for budget overruns, API failures

### Operator Dashboard
- **Real-time:** RQ job queue status (pending, active, failed)
- **Daily summary:** Videos generated, cost, cache hit rate
- **Approval queue:** First-time templates awaiting review
- **A/B test results:** Video vs text-only engagement comparison

---

## Deployment Strategy

### MVP Deployment (Local)
```bash
# 1. Install dependencies
uv sync
brew install redis ffmpeg  # macOS

# 2. Start services
redis-server &
uv run rq worker video_generation &
uv run uvicorn api.main:app --reload &
cd web && npm run dev &

# 3. Verify
curl http://localhost:8000/api/health
curl http://localhost:3000
```

### Production Deployment (Future)
```bash
# Docker Compose
docker-compose up -d

# Services:
# - FastAPI (port 8000)
# - Next.js (port 3000)
# - Redis (port 6379)
# - RQ Worker (background)
# - NiceGUI Operator Dashboard (port 8080)
```

---

## Testing Strategy

### Unit Tests
- **video_generator.py:** Mock SORA client, test retries/timeouts
- **video_cache.py:** fakeredis, test hit/miss/TTL
- **video_worker.py:** Test fallback chain, idempotency
- **cost_management.py:** Test budget enforcement, operator override

### Integration Tests
- **Full pipeline:** Enqueue → Worker → Cache → Serve
- **API endpoints:** POST /videos/generate → GET /videos/status
- **Fallback chain:** SORA fail → Infographic → Text

### Quality Validation
- **Video validation:** ffprobe checks (resolution, duration, codec)
- **Template validation:** Prohibited language scan, visual metaphor check

### Mobile Testing
- **Devices:** iPhone 13, Pixel 6, iPad Air
- **Browsers:** Safari, Chrome, Firefox
- **Scenarios:** Playback, touch controls, landscape mode, slow 3G

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SORA API unavailable | Medium | High | Aggressive caching (95%+ hit rate) + infographic fallback |
| Cost overrun | Low | Medium | Daily budget caps ($5/day) + alerts at 80% |
| Video quality issues | Medium | Medium | Automated validation + operator approval queue |
| Mobile playback failures | Low | High | Extensive mobile testing + `playsInline` attribute |
| Cache storage growth | Low | Low | LRU eviction at 5GB + 30-day TTL |
| Worker queue backlog | Low | Medium | Priority queues + multiple workers |

---

## Future Enhancements (Post-MVP)

### Phase 4: Advanced Features (Month 2)
- **Personalized videos:** Inject user-specific data (e.g., actual card number, balances)
- **Multi-language:** Generate videos in Spanish, Mandarin
- **Interactive videos:** Clickable hotspots, choose-your-own-adventure
- **Live preview:** Real-time SORA generation status updates (WebSocket)

### Phase 5: Scale & Optimize (Month 3)
- **CDN integration:** CloudFlare for global video delivery
- **Video compression:** H.265 codec, adaptive bitrate streaming
- **Predictive caching:** Pre-generate videos for likely recommendations
- **A/B test automation:** Auto-pause low-performing video variants

### Phase 6: Advanced Analytics (Month 4)
- **Heatmaps:** Track user attention within videos
- **Engagement scoring:** ML model predicts video effectiveness
- **Recommendation optimization:** Use video engagement to improve persona assignment

---

## References

- **Chunk 1 Details:** `docs/video_generation/CHUNK_1_POC.md`
- **Chunk 2 Details:** `docs/video_generation/CHUNK_2_SCALEOUT.md`
- **Chunk 3 Details:** `docs/video_generation/CHUNK_3_UX_OPS.md`
- **OpenAI SORA Docs:** https://openai.com/sora (when available)
- **RQ Documentation:** https://python-rq.org/
- **Next.js Video Optimization:** https://nextjs.org/docs/app/building-your-application/optimizing/videos

---

**Last Updated:** 2025-01-05
**Author:** Claude Code (SpendSense Team)
**Version:** 1.0 (Initial Architecture)
