# Chunk 1: Core SORA Integration POC (Weeks 1-2)

**Objective:** Prove end-to-end SORA video generation works for one topic/persona with traceability.

**Timeline:** Weeks 1-2 (10 business days)
**Scope:** Backend only, single topic (credit_utilization), High Utilization persona, manual test runs
**Deliverables:** 5 test videos + trace JSONs + unit tests

---

## Success Criteria

- ✅ Runtime: <30s per video
- ✅ Quality: 720p minimum, 5-10 seconds duration  
- ✅ Trace JSON includes valid video URLs
- ✅ 8 unit tests + 2 integration tests passing
- ✅ 5 manual test videos generated successfully

---

## Architecture Decisions

### 1. SORA API Client: Synchronous vs Async

**Decision:** Use synchronous API client with retry decorator

**Rationale:**
- Existing codebase uses synchronous patterns (SQLite, Parquet I/O)
- POC runs manual tests (no concurrency needed)
- Simpler error handling and debugging
- Can upgrade to async in Chunk 3 for background jobs

**Implementation:**
```python
class SORAVideoGenerator:
    def __init__(self, api_key: str, timeout: int = 30):
        self.client = openai.Client(api_key=api_key)
        self.timeout = timeout
    
    @retry(max_attempts=3, backoff_seconds=2)
    def generate_video(self, prompt: str, metadata: Dict) -> Dict[str, Any]:
        """Generate video with retries, return {video_url, metadata}"""
```

---

### 2. Error Handling Strategy

**Decision:** Graceful degradation with fallback placeholders

**Error Handling Tiers:**
1. **API Errors (timeout, rate limit):** Retry with exponential backoff (3 attempts)
2. **Generation Failures:** Return `{"video_url": null, "error": "reason", "fallback": "static_image_url"}`
3. **Configuration Errors:** Raise exception at initialization (fail fast)

**Trace Logging:**
```json
{
  "video_generation": {
    "timestamp": "2025-11-05T10:00:00Z",
    "status": "failed",
    "error": "SORA API timeout after 30s",
    "retry_count": 3,
    "fallback_used": true
  }
}
```

---

### 3. Configuration Management

**Decision:** Extend existing constants.py pattern with environment variables

Add to `/Users/caseymanos/GauntletAI/SpendSense/ingest/constants.py` (line 237):

```python
# Video Generation Configuration
VIDEO_GENERATION_CONFIG = {
    "enabled": os.getenv("SORA_ENABLED", "false").lower() == "true",
    "api_key": os.getenv("SORA_API_KEY", ""),
    "model": "sora-1.0-turbo",
    "resolution": "720p",
    "duration_seconds": (5, 10),  # min, max
    "timeout_seconds": 30,
    "max_retries": 3,
    "retry_backoff_seconds": 2,
    "storage_path": "data/videos",
    "fallback_image_url": "https://placeholder.co/720x480/png?text=Video+Unavailable"
}
```

---

### 4. Storage Strategy (Manual POC Phase)

**Decision:** Store URLs only, no local video files

**Rationale:**
- SORA returns hosted URLs (no download required)
- Reduces storage complexity for POC
- Trace JSON already stores all metadata
- Can add download capability in Chunk 2 if needed

---

## Task Breakdown

### Phase 1: Foundation (Tasks 1-4, ~6 hours)

#### Task 1: Create video_generator.py module
**File:** `recommend/video_generator.py`
**Time:** 2 hours

**Acceptance Criteria:**
- [ ] `SORAVideoGenerator` class with `__init__(api_key, timeout)`
- [ ] `generate_video(prompt, metadata)` method returns `Dict[str, Any]`
- [ ] Retry decorator with exponential backoff (3 attempts, 2s initial)
- [ ] Timeout enforcement using `openai.timeout` parameter
- [ ] Error handling returns structured error dict
- [ ] Logging with timestamps and retry counts

**Implementation Notes:**
```python
from pathlib import Path
import openai
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SORAVideoGenerator:
    def __init__(self, api_key: str, timeout: int = 30):
        if not api_key:
            raise ValueError("SORA API key required")
        self.client = openai.Client(api_key=api_key)
        self.timeout = timeout
        
    def generate_video(self, prompt: str, metadata: Dict) -> Dict[str, Any]:
        try:
            response = self.client.sora.generate(
                prompt=prompt,
                timeout=self.timeout,
                **metadata
            )
            return {
                "video_url": response.url,
                "duration": response.duration,
                "resolution": response.resolution,
                "generated_at": response.created_at
            }
        except openai.Timeout:
            logger.error(f"SORA API timeout after {self.timeout}s")
            return {"video_url": None, "error": "timeout"}
        except Exception as e:
            logger.error(f"SORA generation failed: {e}")
            return {"video_url": None, "error": str(e)}
```

---

#### Task 2: Create prompt_templates.py module
**File:** `recommend/prompt_templates.py`
**Time:** 2 hours

**Visual Specification (credit_utilization prompt):**
```
Visual: Clean, educational animation showing:
- Credit card with utilization meter filling from 73% to 28%
- Pressure gauge showing stress reduction
- Warning indicators (red→yellow→green transition)
- Simple bar chart showing balance reduction over time

Style: Calm blues and greens, minimalist design, supportive tone.
No faces, no text overlays (accessibility).
Duration: 8 seconds.
```

**Template Structure:**
```python
from typing import Dict, Any

PROMPT_TEMPLATES = {
    "high_utilization": {
        "credit_utilization": {
            "visual_description": """
Create an 8-second educational animation about credit utilization.

Scene: Credit card visual with transparent meter showing {utilization_pct}% filled (red zone).

Animation sequence:
1. (0-2s) Card meter pulses red at {utilization_pct}%
2. (2-5s) Meter slowly decreases to 28%, color transitions red → orange → green
3. (5-8s) Credit score number increases from 650 to 720 with upward arrow

Visual style:
- Clean, modern 2D motion graphics
- Color scheme: Red (#EF4444) to Green (#22C55E)
- No human characters, minimalist icons only

Text overlay (final 2 seconds): "Below 30% = Better Score"

Mood: Educational, empowering, urgent but hopeful.
""",
            "duration_seconds": 8,
            "tone": "supportive, educational",
            "tags": ["credit", "utilization", "debt_reduction"]
        }
    }
}

def build_video_prompt(topic: str, persona: str, user_context: Dict) -> str:
    """Merge template with user data (utilization_pct, card_mask)"""
    template = PROMPT_TEMPLATES.get(persona, {}).get(topic)
    if not template:
        raise ValueError(f"No template for {persona}:{topic}")
    
    # Inject user data
    prompt = template["visual_description"].format(
        utilization_pct=int(user_context.get("credit_max_util_pct", 50))
    )
    return prompt
```

---

#### Task 3: Add VIDEO_GENERATION_CONFIG to constants.py
**File:** `ingest/constants.py`
**Line:** Add after line 236
**Time:** 0.5 hours

(See Configuration Management section above)

---

#### Task 4: Create SORA mock for testing
**File:** `tests/mocks/sora_mock.py`
**Time:** 1.5 hours

```python
import time
import hashlib
from typing import Dict, Optional
from datetime import datetime

class MockVideoResponse:
    def __init__(self, url: str, duration: int, resolution: str):
        self.url = url
        self.duration = duration
        self.resolution = resolution
        self.created_at = datetime.now().isoformat()

class MockSORAClient:
    def __init__(self, simulate_error: Optional[Exception] = None, delay_seconds: float = 0.5):
        self.simulate_error = simulate_error
        self.delay_seconds = delay_seconds
        self.generation_count = 0
    
    def generate(self, prompt: str, **kwargs) -> MockVideoResponse:
        self.generation_count += 1
        
        # Simulate latency
        time.sleep(self.delay_seconds)
        
        # Simulate errors
        if self.simulate_error:
            raise self.simulate_error
        
        # Return deterministic video URL
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        return MockVideoResponse(
            url=f"https://mock-sora.test/v/{prompt_hash}",
            duration=8,
            resolution="720p"
        )
```

---

### Phase 2: Integration (Tasks 5-7, ~8 hours)

#### Task 5: Integrate video generation into recommendation engine
**File:** `recommend/engine.py`
**Time:** 3 hours

**Modifications:**

1. **Line 20:** Add import
```python
from recommend.video_generator import SORAVideoGenerator
from recommend.prompt_templates import build_video_prompt
from ingest.constants import VIDEO_GENERATION_CONFIG
```

2. **Line 42:** Initialize generator
```python
VIDEO_GENERATOR = None
if VIDEO_GENERATION_CONFIG["enabled"]:
    VIDEO_GENERATOR = SORAVideoGenerator(
        api_key=VIDEO_GENERATION_CONFIG["api_key"],
        timeout=VIDEO_GENERATION_CONFIG["timeout_seconds"]
    )
```

3. **Line 314-328:** Modify `_select_education_items()`
```python
# After line 327 (before return)
if VIDEO_GENERATOR and item.get("topic") == "credit_utilization":
    try:
        prompt = build_video_prompt(
            topic=item["topic"],
            persona=persona,
            user_context=user_context
        )
        video_data = VIDEO_GENERATOR.generate_video(prompt, {})
        rec["video_url"] = video_data.get("video_url")
        rec["video_metadata"] = {
            "duration": video_data.get("duration"),
            "resolution": video_data.get("resolution"),
            "generated_at": video_data.get("generated_at")
        }
    except Exception as e:
        # Graceful degradation - log error but continue
        logger.warning(f"Video generation failed: {e}")
        rec["video_url"] = None
        rec["video_error"] = str(e)
```

4. **Line 859-901:** Modify `_save_trace()` to include video metadata

---

#### Task 6: Update trace JSON schema
**File:** `docs/traces/user_0001.json` (example)
**Time:** 1 hour

**New Structure:**
```json
{
  "recommendations": {
    "recommendations": [
      {
        "type": "education",
        "title": "Understanding Credit Utilization",
        "video_url": "https://sora.openai.com/v/abc123",
        "video_metadata": {
          "duration_seconds": 8,
          "resolution": "720p",
          "generated_at": "2025-11-05T10:00:00Z",
          "prompt_hash": "sha256:1a2b3c4d",
          "generation_time_seconds": 12.4
        }
      }
    ]
  },
  "video_generation_log": [
    {
      "timestamp": "2025-11-05T10:00:00Z",
      "topic": "credit_utilization",
      "status": "success",
      "video_url": "https://sora.openai.com/v/abc123",
      "generation_time_seconds": 12.4
    }
  ]
}
```

---

#### Task 7: Create manual test runbook
**File:** `docs/video_generation_runbook.md`
**Time:** 2 hours

```markdown
# Video Generation Manual Test Runbook

## Prerequisites
1. OpenAI API key with SORA access
2. Export `SORA_API_KEY` and `SORA_ENABLED=true`

## Test Case 1: Generate video for user_0001 (high utilization)
1. Run: `uv run python -c "from recommend.engine import generate_recommendations; print(generate_recommendations('user_0001'))"`
2. Verify: Output includes `video_url` field
3. Check trace: `cat docs/traces/user_0001.json | jq '.video_generation_log'`
4. Expected: URL like `https://sora.openai.com/v/...`

## Repeat for users: 0001, 0004, 0007, 0012, 0015

## Success Criteria
- [ ] All 5 videos generated successfully
- [ ] All URLs return 200 status
- [ ] Video duration: 5-10 seconds
- [ ] Resolution: 720p
- [ ] Generation time: <30s per video
```

---

### Phase 3: Testing & Validation (Tasks 8-10, ~6 hours)

#### Task 8: Create test_video_generation.py
**File:** `tests/test_video_generation.py`
**Time:** 3 hours

```python
import pytest
from recommend.video_generator import SORAVideoGenerator
from recommend.prompt_templates import build_video_prompt
from tests.mocks.sora_mock import MockSORAClient

class TestSORAVideoGenerator:
    def test_initialization_with_valid_api_key(self):
        generator = SORAVideoGenerator(api_key="test-key")
        assert generator.api_key == "test-key"
        
    def test_initialization_fails_without_api_key(self):
        with pytest.raises(ValueError):
            SORAVideoGenerator(api_key="")
    
    def test_generate_video_success(self):
        generator = SORAVideoGenerator(api_key="test-key")
        generator.client = MockSORAClient()
        
        result = generator.generate_video("Test prompt", {})
        assert result["video_url"] is not None
        assert result["video_url"].startswith("https://")
        
    def test_generate_video_timeout(self):
        generator = SORAVideoGenerator(api_key="test-key", timeout=1)
        generator.client = MockSORAClient(delay_seconds=2)
        
        result = generator.generate_video("Test prompt", {})
        assert result["video_url"] is None
        assert "timeout" in result["error"]

class TestPromptTemplates:
    def test_build_prompt_with_user_data(self):
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={"credit_max_util_pct": 73.5}
        )
        assert "73%" in prompt
        assert "Credit card" in prompt
```

---

#### Task 9: Generate 5 test videos manually
**File:** Manual execution following runbook
**Time:** 2 hours

**Documentation:** Save results in `docs/video_test_results.md`:
```markdown
| User ID | Video URL | Duration | Resolution | Gen Time | Status |
|---------|-----------|----------|------------|----------|--------|
| user_0001 | https://... | 8s | 720p | 14.2s | ✅ |
| user_0004 | https://... | 7s | 720p | 12.8s | ✅ |
| user_0007 | https://... | 8s | 720p | 15.1s | ✅ |
| user_0012 | https://... | 9s | 720p | 13.4s | ✅ |
| user_0015 | https://... | 8s | 720p | 14.7s | ✅ |
```

---

#### Task 10: Update documentation
**Files:** `docs/decision_log.md`, `docs/schema.md`, `README.md`
**Time:** 1 hour

**Decision Log Entry:**
```markdown
## Decision 58: SORA API Client Architecture (Sync vs Async)

**Context:** Video generation adds I/O latency to recommendation flow.

**Decision:** Use synchronous API client with retry decorator.

**Rationale:**
- Existing codebase uses synchronous patterns
- POC runs manual tests (no concurrency needed)
- Simpler error handling and debugging
- Can upgrade to async in Chunk 3 for background jobs

**Alternatives Considered:**
- Async with asyncio: Adds complexity for no POC benefit
- Celery queue: Over-engineered for single-topic POC

**Status:** Implemented in recommend/video_generator.py
```

---

## Data Flow Diagram

```
┌──────────────┐
│ User Request │
│ (user_id)    │
└──────┬───────┘
       │
       v
┌─────────────────────────┐
│ generate_recommendations│  (engine.py:83)
│ (user_id)               │
└──────┬──────────────────┘
       │
       │ 1. Load user context
       v
┌───────────────────────────┐
│ _load_user_context()      │  (engine.py:185)
│ - SQLite (users, accounts)│
│ - Parquet (signals.parquet)│
│ - Transactions            │
└──────┬────────────────────┘
       │
       │ 2. Select education items
       v
┌───────────────────────────┐
│ _select_education_items() │  (engine.py:276)
│ - Filter by persona       │
│ - Check eligibility       │
│ - Score relevance         │
└──────┬────────────────────┘
       │
       │ 3. For credit_utilization items only
       v
┌────────────────────────────┐
│ VIDEO GENERATION (NEW)     │
├────────────────────────────┤
│ 1. Build prompt            │  prompt_templates.py
│    - Get template          │
│    - Insert user data      │
│    - Add visual specs      │
│                            │
│ 2. Call SORA API           │  video_generator.py
│    - Retry logic (3x)      │
│    - Timeout (30s)         │
│    - Return URL + metadata │
│                            │
│ 3. Handle errors           │
│    - Graceful degradation  │
│    - Fallback image        │
│    - Log to trace          │
└──────┬─────────────────────┘
       │
       │ 4. Add video_url to recommendation
       v
┌───────────────────────────┐
│ Recommendation Object     │
├───────────────────────────┤
│ {                         │
│   "type": "education",    │
│   "title": "...",         │
│   "video_url": "https://",│ ← NEW
│   "video_metadata": {...} │ ← NEW
│ }                         │
└──────┬────────────────────┘
       │
       │ 5. Save trace
       v
┌───────────────────────────┐
│ _save_trace()             │  (engine.py:859)
│ - Append to trace JSON    │
│ - Add video_generation_log│ ← NEW
└───────────────────────────┘
```

---

## Open Questions

### 1. SORA API Access
**Question:** Do we have confirmed access to OpenAI SORA API?
**Resolution:** Start with mock API to validate architecture, swap in real API when access confirmed.

### 2. Video URL Persistence
**Question:** How long are SORA-generated video URLs valid?
**Resolution:** Ask OpenAI support. Implement download capability as optional flag if temporary.

### 3. Cost Management
**Question:** What is per-video cost?
**Resolution:** Check OpenAI SORA pricing (estimated $0.05-0.10/video for POC).

---

## File Checklist

### Files to Create
- [ ] `recommend/video_generator.py` (~200 lines)
- [ ] `recommend/prompt_templates.py` (~150 lines)
- [ ] `tests/mocks/sora_mock.py` (~120 lines)
- [ ] `tests/test_video_generation.py` (~300 lines)
- [ ] `docs/video_generation_runbook.md` (~100 lines)
- [ ] `docs/video_test_results.md` (~50 lines)
- [ ] `tests/mocks/__init__.py` (~5 lines)

### Files to Modify
- [ ] `recommend/engine.py` (~50 lines added)
- [ ] `ingest/constants.py` (~25 lines added)
- [ ] `docs/decision_log.md` (~80 lines added)
- [ ] `docs/schema.md` (~40 lines added)
- [ ] `README.md` (~30 lines added)
- [ ] `requirements.txt` (~2 lines added: `openai>=1.0.0`)

**Total:** ~1,767 lines of code

---

**Next Steps:** After Chunk 1 completion, proceed to Chunk 2 (Scale-out Infrastructure)
