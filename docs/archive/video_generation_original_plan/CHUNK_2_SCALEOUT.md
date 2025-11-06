# Chunk 2: Scale-out Infrastructure + API (Weeks 3-4)

**Objective:** Scale from 1 topic to 20 templates (4 personas × 5 topics), add caching + background jobs.

**Timeline:** Weeks 3-4 (10 business days)
**Scope:** Background workers (Redis+RQ), API endpoints, cache, 20 prompt templates, persona-driven generation hook
**Dependencies:** Chunk 1 POC complete

---

## Success Criteria

- ✅ Cache hit rate >75% in steady state
- ✅ Background jobs never block user requests
- ✅ All 20 templates validated with sample outputs
- ✅ 15+ tests passing (cache, worker, integration, templates)
- ✅ API endpoints functional (<100ms response time)

---

## Key Architectural Decisions

### 1. Background Job System: Redis + RQ (not Celery)

**Decision:** Use Redis Queue (RQ) for background job processing

**Rationale:**
- **Simpler:** Fewer moving parts than Celery (no broker+backend split)
- **Python-native:** Direct Python function calls (no serialization complexity)
- **Lightweight:** Perfect for MVP (100 users, ~300 videos max)
- **Easy monitoring:** Built-in job status, result storage, failure tracking

**Comparison:**
| Feature | RQ | Celery |
|---------|----|----|
| Setup complexity | Low (Redis only) | High (Redis/RabbitMQ + backend) |
| Learning curve | Minimal | Steep |
| Concurrency | Process-based | Process/thread/eventlet |
| MVP fit | ✅ Excellent | ❌ Over-engineered |

---

### 2. Cache Key Design: Persona + Topic (NOT user-specific)

**Decision:** Hash cache key from `persona:topic` only

**Rationale:**
- **Maximizes cache hits:** 100 users × 3 recs = only 20 unique videos needed (4 personas × 5 topics)
- **Generic educational content:** Videos teach concepts, not personalized to user data
- **Cost optimization:** Generate once, serve to all matching users
- **Target hit rate:** 75-85% (95%+ after initial generation phase)

**Cache Key Formula:**
```python
cache_key = sha256(f"{persona}:{topic}")[:16]
# Example: "high_utilization:credit_utilization" → "a3f2b8c9d1e4f7a2"
```

---

### 3. Storage Architecture: Redis + Filesystem

**Decision:** Dual storage (Redis for metadata, filesystem for video files)

**Why NOT database?**
- SQLite would bloat with binary video data
- Filesystem handles large files efficiently
- Redis provides fast lookups with built-in TTL

**Storage Paths:**
```
data/videos/
├── high_utilization/
│   ├── credit_utilization/
│   │   └── a3f2b8c9.mp4
│   └── debt_paydown_strategy/
├── variable_income/
├── subscription_heavy/
└── savings_builder/
```

---

### 4. Fallback Chain: SORA → Static Infographic → Text

**Decision:** Three-tier fallback with automated degradation

**Chain:**
1. **SORA API (Primary):** Best quality, dynamic animation
2. **Static Infographic (Secondary):** SVG templates, fast generation
3. **Text-only (Fallback):** Existing recommendation cards, 100% reliable

**Cost Controls:**
- Generate only top 3 recommendations per user
- Skip "general" persona (no recommendations)
- Daily budget cap: $5/day ($150/month)

---

## 20 Prompt Templates

### High Utilization Persona (5 topics)

#### 1. credit_utilization
- **Visual:** Credit cards stacking like domino tiles with percentages
- **Prompt:** "Educational animation showing credit utilization concept. Credit cards with percentage meters, green zone (<30%), yellow (30-50%), red (>50%). Supportive tone, no shame."
- **Duration:** 15s

#### 2. debt_paydown_strategy
- **Visual:** Two paths diverging - "Avalanche" (mountain) vs "Snowball" (rolling snow)
- **Prompt:** "Split-screen animation comparing debt avalanche vs snowball. Show balance decreasing charts. Encouraging, educational."
- **Duration:** 20s

#### 3. autopay_setup
- **Visual:** Calendar with automatic checkmarks appearing on due dates
- **Prompt:** "Animation of autopay workflow: bill arrives → autopay triggers → payment sent. Show peace of mind. Calm, reassuring tone."
- **Duration:** 15s

#### 4. balance_transfer
- **Visual:** Interest meter draining from full to empty
- **Prompt:** "Balance transfer visualization: credit card balance moving to 0% card, interest meter drops. Show savings. Clear, factual tone."
- **Duration:** 18s

#### 5. interest_calculation
- **Visual:** Money counter ticking up daily (daily periodic rate)
- **Prompt:** "How credit card interest compounds daily. Show APR converting to daily rate, balance growing. Educational, eye-opening but supportive."
- **Duration:** 20s

### Variable Income Persona (5 topics)

#### 6. variable_income_budgeting
- **Visual:** Income bars of varying heights with percentage slices (50/30/20 rule)
- **Prompt:** "Percentage-based budgeting animation. Income bars vary, percentages stay consistent. Show flexibility adapting to fluctuations."
- **Duration:** 18s

#### 7. emergency_fund_basics
- **Visual:** Safety net catching falling coins, expanding with deposits
- **Prompt:** "Emergency fund building animation. Safety net grows as coins fall in. Show 3-6 month coverage threshold. Calm, reassuring."
- **Duration:** 15s

#### 8. percent_based_budgets
- **Visual:** Pie chart reshaping with income changes, slices stay proportional
- **Prompt:** "Pie chart budget adapting to income changes. $2K vs $4K paycheck, percentages constant. Practical, supportive."
- **Duration:** 15s

#### 9. income_smoothing
- **Visual:** Bumpy income line smoothing into flat "virtual paycheck" line
- **Prompt:** "Income smoothing visualization. Bumpy deposits into holding tank, flat withdrawals emerge. Show consistency achieved."
- **Duration:** 18s

#### 10. cash_buffer
- **Visual:** Water tank with level indicators (months of expenses)
- **Prompt:** "Cash buffer as water tank. Deposits raise level, expenses drain. Target: 1-2 month buffer. Practical, encouraging."
- **Duration:** 15s

### Subscription Heavy Persona (5 topics)

#### 11. subscription_audit
- **Visual:** Receipts flying out of wallet, sorted into "keep" and "cancel" piles
- **Prompt:** "Subscription audit animation. Receipts categorize into essentials vs nice-to-haves. Show savings counter. Actionable, non-judgmental."
- **Duration:** 20s

#### 12. cancellation_tips
- **Visual:** Cancellation button maze (show it's often hidden)
- **Prompt:** "How to cancel subscriptions: navigate through typical UI patterns. Show common hiding spots. Empowering, helpful."
- **Duration:** 18s

#### 13. bill_alerts
- **Visual:** Phone receiving notifications before each recurring charge
- **Prompt:** "Bill alert setup. Phone receives warning 3 days before charge. Show peace of mind, no surprises. Calm, protective."
- **Duration:** 15s

#### 14. recurring_spend_tracking
- **Visual:** Monthly calendar with recurring charges highlighted
- **Prompt:** "Tracking recurring spend: calendar highlights patterns. Show hidden costs adding up. Eye-opening but supportive."
- **Duration:** 18s

#### 15. subscription_consolidation
- **Visual:** Multiple service logos merging into bundled packages
- **Prompt:** "Subscription bundling: separate services combining into discounted bundles. Show savings calculation. Smart, strategic."
- **Duration:** 15s

### Savings Builder Persona (5 topics)

#### 16. goal_setting
- **Visual:** Target goal with progress bar filling up over time
- **Prompt:** "Savings goal visualization: target amount, progress bar fills with deposits. Show milestone celebrations. Motivating, positive."
- **Duration:** 18s

#### 17. automation_setup
- **Visual:** Paycheck arriving, splitting automatically into accounts
- **Prompt:** "Automated savings: paycheck splits on arrival (checking/savings/investment). Show 'pay yourself first'. Smooth, effortless."
- **Duration:** 15s

#### 18. hysa_comparison
- **Visual:** Two bank buildings with interest rate meters
- **Prompt:** "HYSA vs regular savings. Show interest earned over 1 year on same balance. Eye-opening, factual."
- **Duration:** 15s

#### 19. cd_basics
- **Visual:** Money locked in vault with countdown timer, interest accumulating
- **Prompt:** "CD basics: money locked for term, higher interest accumulates. Show trade-off: liquidity vs returns. Educational, clear."
- **Duration:** 20s

#### 20. savings_rate_optimization
- **Visual:** Slider adjusting savings percentage, future balance projection updates
- **Prompt:** "Optimizing savings rate: slider from 5% to 20%, show projections at 1yr, 5yr, 10yr. Motivating, empowering."
- **Duration:** 18s

---

## Task Breakdown

### Phase 1: Foundation (Days 1-2)

#### Task 1.1: Create video templates module
**File:** `recommend/video_templates.py`
**Time:** 4 hours

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class VideoTemplate:
    persona: str
    topic: str
    prompt_template: str
    visual_metaphor: str
    duration_seconds: int = 15
    style: str = "educational, supportive"
    fallback_static: str = "templates/default.svg"

VIDEO_TEMPLATES: Dict[str, Dict[str, VideoTemplate]] = {
    "high_utilization": {
        "credit_utilization": VideoTemplate(
            persona="high_utilization",
            topic="credit_utilization",
            prompt_template="Educational animation showing...",
            visual_metaphor="Credit card meter from red to green",
            duration_seconds=15
        ),
        # ... 4 more topics
    },
    "variable_income": { ... },  # 5 topics
    "subscription_heavy": { ... },  # 5 topics
    "savings_builder": { ... }  # 5 topics
}

def get_template(persona: str, topic: str) -> VideoTemplate:
    """Get template with validation"""
    if persona not in VIDEO_TEMPLATES:
        raise ValueError(f"Unknown persona: {persona}")
    if topic not in VIDEO_TEMPLATES[persona]:
        raise ValueError(f"Unknown topic: {topic} for {persona}")
    return VIDEO_TEMPLATES[persona][topic]
```

---

#### Task 1.2: Implement video cache system
**File:** `recommend/video_cache.py`
**Time:** 6 hours

```python
import hashlib
import redis
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

class VideoCache:
    def __init__(self, redis_client: redis.Redis, base_path: Path):
        self.redis = redis_client
        self.base_path = base_path
        self.ttl_seconds = 30 * 24 * 3600  # 30 days
        
    def _generate_key(self, persona: str, topic: str) -> str:
        """Generate cache key from persona+topic"""
        raw = f"{persona}:{topic}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def get(self, persona: str, topic: str) -> Optional[Dict]:
        """Read-through cache lookup"""
        cache_key = self._generate_key(persona, topic)
        cached_data = self.redis.hgetall(f"video:{cache_key}")
        
        if not cached_data:
            return None
            
        # Check TTL
        created_at = datetime.fromisoformat(cached_data[b'created_at'].decode())
        age_seconds = (datetime.now() - created_at).total_seconds()
        
        if age_seconds > self.ttl_seconds:
            self.redis.delete(f"video:{cache_key}")
            return None
            
        return {
            "status": cached_data[b'status'].decode(),
            "url": cached_data[b'url'].decode(),
            "created_at": cached_data[b'created_at'].decode(),
            "cache_age_seconds": int(age_seconds),
            "hash": cached_data[b'hash'].decode()
        }
    
    def set(self, persona: str, topic: str, video_hash: str, 
            url: str, status: str = "ready") -> None:
        """Store video metadata in cache"""
        cache_key = self._generate_key(persona, topic)
        
        self.redis.hset(f"video:{cache_key}", mapping={
            "status": status,
            "url": url,
            "hash": video_hash,
            "created_at": datetime.now().isoformat(),
            "persona": persona,
            "topic": topic
        })
        
        self.redis.expire(f"video:{cache_key}", self.ttl_seconds)
```

---

#### Task 1.3: Set up Redis infrastructure
**Time:** 1 hour

```bash
# Install Redis
brew install redis  # macOS
# or: apt install redis  # Linux

# Add to requirements.txt
echo "redis>=5.0.0" >> requirements.txt
echo "rq>=1.15.0" >> requirements.txt

# Start Redis
redis-server &
```

---

### Phase 2: Worker Implementation (Days 3-5)

#### Task 2.3: Implement main worker job function
**File:** `recommend/video_worker.py`
**Time:** 6 hours

```python
import os
import logging
from pathlib import Path
from typing import Dict
import hashlib
import redis
from rq import Queue

from recommend.video_cache import VideoCache
from recommend.video_templates import get_template

logger = logging.getLogger(__name__)

def generate_video_job(persona: str, topic: str, job_id: str) -> Dict:
    """
    RQ worker job: Generate video for persona+topic.
    
    Returns:
        {"status": "success"|"failed", "url": "...", "hash": "...", "fallback_used": "sora"|"static"|"text"}
    """
    # Initialize cache
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    cache = VideoCache(redis_client, Path("data/videos"))
    
    # IDEMPOTENCY CHECK
    cached = cache.get(persona, topic)
    if cached and cached["status"] == "ready":
        logger.info(f"Video already cached for {persona}:{topic}")
        return {
            "status": "success",
            "url": cached["url"],
            "hash": cached["hash"],
            "fallback_used": "cache"
        }
    
    # Mark as processing
    cache.set_processing(persona, topic, job_id)
    
    try:
        # Get template
        template = get_template(persona, topic)
        prompt = template.prompt_template
        
        # FALLBACK CHAIN: SORA → Static → Text
        video_bytes = None
        fallback_used = None
        
        # Try SORA first
        try:
            logger.info(f"Attempting SORA generation for {persona}:{topic}")
            from recommend.video_generator import SORAVideoGenerator
            sora_client = SORAVideoGenerator(api_key=os.getenv("OPENAI_API_KEY"))
            video_data = sora_client.generate_video(prompt, {})
            
            if video_data.get("video_url"):
                # SORA returns URL - download video bytes for local storage
                import requests
                response = requests.get(video_data["video_url"], timeout=60)
                video_bytes = response.content
                fallback_used = "sora"
        except Exception as e:
            logger.warning(f"SORA failed for {persona}:{topic}: {e}")
            
            # Try static infographic
            try:
                from recommend.infographic_generator import generate_static_infographic
                logger.info(f"Falling back to static infographic for {persona}:{topic}")
                video_bytes = generate_static_infographic(template)
                fallback_used = "static"
            except Exception as e2:
                logger.warning(f"Static fallback failed: {e2}")
                fallback_used = "text"
                # Return text-only (no video)
                return {
                    "status": "failed",
                    "fallback_used": "text",
                    "error": str(e)
                }
        
        # Generate hash
        video_hash = hashlib.sha256(video_bytes).hexdigest()[:16]
        
        # Save to disk
        video_dir = Path("data/videos") / persona / topic
        video_dir.mkdir(parents=True, exist_ok=True)
        video_path = video_dir / f"{video_hash}.mp4"
        
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        
        # Update cache
        url = f"/videos/{persona}/{topic}/{video_hash}.mp4"
        cache.set(persona, topic, video_hash, url, status="ready")
        
        return {
            "status": "success",
            "url": url,
            "hash": video_hash,
            "fallback_used": fallback_used
        }
        
    except Exception as e:
        logger.error(f"Video generation failed for {persona}:{topic}: {e}")
        cache.mark_failed(persona, topic, str(e))
        
        return {
            "status": "failed",
            "error": str(e)
        }
```

---

### Phase 3: Job Enqueuing (Days 5-6)

#### Task 3.1: Implement job enqueue module
**File:** `recommend/video_enqueue.py`
**Time:** 3 hours

```python
import os
import logging
from pathlib import Path
import redis
from rq import Queue

from recommend.video_cache import VideoCache
from recommend.video_worker import generate_video_job

logger = logging.getLogger(__name__)

def enqueue_video_generation(persona: str, topic: str) -> str:
    """
    Enqueue video generation job for persona+topic.
    
    Returns:
        Job ID or "cached"/"skipped"
    """
    # Skip general persona
    if persona == "general":
        return "skipped"
    
    # Initialize cache and queue
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    cache = VideoCache(redis_client, Path("data/videos"))
    queue = Queue("video_generation", connection=redis_client)
    
    # Check cache first
    cached = cache.get(persona, topic)
    if cached and cached["status"] == "ready":
        return "cached"
    
    # Enqueue job
    job = queue.enqueue(
        generate_video_job,
        persona=persona,
        topic=topic,
        job_id="pending",
        job_timeout="10m",
        result_ttl=3600
    )
    
    cache.set_processing(persona, topic, job.id)
    logger.info(f"Enqueued job {job.id} for {persona}:{topic}")
    return job.id
```

---

#### Task 3.2: Integrate with persona assignment flow
**File:** `personas/assignment.py` (line 301)
**Time:** 1 hour

```python
# After recommendation generation (around line 300)
from recommend.video_enqueue import enqueue_videos_for_recommendations

if len(result.get("recommendations", [])) > 0:
    rec_count += 1
    # NEW: Enqueue video generation jobs
    enqueue_videos_for_recommendations(user_id, result["recommendations"])
```

---

### Phase 4: API Endpoints (Days 7-8)

#### Task 4.2: Implement video generation endpoint
**File:** `api/main.py` (after line 127)
**Time:** 2 hours

```python
from api.models import VideoGenerationRequest
from recommend.video_enqueue import enqueue_video_generation

@app.post("/videos/generate", tags=["Videos"])
async def generate_video(request: VideoGenerationRequest):
    """Enqueue video generation job"""
    job_id = enqueue_video_generation(request.persona, request.topic)
    
    return {
        "job_id": job_id,
        "status": "enqueued" if job_id not in ["cached", "skipped"] else job_id,
        "persona": request.persona,
        "topic": request.topic
    }

@app.get("/videos/status/{persona}/{topic}", tags=["Videos"])
async def get_video_status(persona: str, topic: str):
    """Check video generation status"""
    import redis
    from recommend.video_cache import VideoCache
    
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    cache = VideoCache(redis_client, Path("data/videos"))
    
    cached = cache.get(persona, topic)
    
    if not cached:
        return {"status": "not_found"}
    
    return {
        "status": cached["status"],
        "url": cached.get("url"),
        "cache_age_seconds": cached.get("cache_age_seconds")
    }
```

---

### Phase 5: Cache Cleanup (Days 9-10)

#### Task 5.2: Implement cleanup orchestrator
**File:** `recommend/video_cleanup.py`
**Time:** 4 hours

```python
import logging
from pathlib import Path
from datetime import datetime, timedelta
import redis

from recommend.video_cache import VideoCache

logger = logging.getLogger(__name__)

DISK_QUOTA_GB = 5
TTL_DAYS = 30

def run_cleanup(dry_run: bool = False) -> Dict:
    """Run cache cleanup tasks"""
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    cache = VideoCache(redis_client, Path("data/videos"))
    
    results = {
        "expired_deleted": 0,
        "orphaned_deleted": 0,
        "lru_evicted": 0,
        "disk_usage_gb": 0.0
    }
    
    # 1. Clean orphaned files
    orphaned = find_orphaned_files(cache)
    for orphan_path in orphaned:
        if not dry_run:
            orphan_path.unlink()
        results["orphaned_deleted"] += 1
    
    # 2. LRU eviction if over quota
    disk_usage_bytes = cache.get_disk_usage()
    disk_usage_gb = disk_usage_bytes / (1024 ** 3)
    results["disk_usage_gb"] = disk_usage_gb
    
    if disk_usage_gb > DISK_QUOTA_GB:
        target_bytes = DISK_QUOTA_GB * (1024 ** 3)
        if not dry_run:
            evicted = cache.evict_lru(target_bytes)
            results["lru_evicted"] = evicted
    
    logger.info(f"Cleanup complete: {results}")
    return results
```

---

## Testing Strategy

### Unit Tests (with fakeredis)

```python
# tests/test_video_cache.py
import fakeredis
from recommend.video_cache import VideoCache

def test_cache_hit():
    redis_client = fakeredis.FakeRedis()
    cache = VideoCache(redis_client, Path("test_videos"))
    
    cache.set("high_utilization", "credit_utilization", "abc123", "/videos/...", "ready")
    
    cached = cache.get("high_utilization", "credit_utilization")
    assert cached is not None
    assert cached["status"] == "ready"

def test_cache_miss():
    redis_client = fakeredis.FakeRedis()
    cache = VideoCache(redis_client, Path("test_videos"))
    
    cached = cache.get("nonexistent", "topic")
    assert cached is None
```

---

## File Structure

```
recommend/
├── video_templates.py       (NEW - 300 lines)
├── video_cache.py           (NEW - 250 lines)
├── video_worker.py          (NEW - 280 lines)
├── video_enqueue.py         (NEW - 150 lines)
├── video_cleanup.py         (NEW - 200 lines)
└── engine.py                (MODIFY - add persona field)

api/
├── main.py                  (MODIFY - add 3 endpoints)
└── models.py                (MODIFY - add 2 models)

tests/
├── test_video_cache.py      (NEW - 200 lines)
├── test_video_worker.py     (NEW - 250 lines)
├── test_video_integration.py(NEW - 150 lines)
└── test_video_templates.py  (NEW - 100 lines)

data/videos/                 (NEW - directory)
```

**Total Code:** ~2,930 lines

---

**Next Steps:** After Chunk 2 completion, proceed to Chunk 3 (UX Integration + Quality + Ops)
