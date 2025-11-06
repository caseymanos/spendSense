# Video Generation Manual Test Runbook

**Purpose:** Manual testing procedure for SORA video generation (Chunk 1 POC)
**Scope:** Single topic (credit_utilization) for high_utilization persona
**Target:** 5 test videos generated successfully
**Timeline:** ~30 minutes

---

## Prerequisites

### 1. OpenAI API Access
- [ ] Confirm SORA API access on OpenAI account
- [ ] Obtain API key with SORA generation permissions
- [ ] Note: If SORA access not available, tests will use mock client

### 2. Environment Setup
```bash
# Set environment variables
export SORA_ENABLED=true
export SORA_API_KEY="sk-your-api-key-here"

# Verify configuration
uv run python -c "from ingest.constants import VIDEO_GENERATION_CONFIG; print(VIDEO_GENERATION_CONFIG)"
```

Expected output:
```python
{
    'enabled': True,
    'api_key': 'sk-...',
    'model': 'sora-1.0-turbo',
    'resolution': '720p',
    'duration_seconds': (5, 10),
    'timeout_seconds': 30,
    'max_retries': 3,
    'retry_backoff_seconds': 2,
    'storage_path': 'data/videos',
    'fallback_image_url': 'https://placeholder.co/720x480/png?text=Video+Unavailable'
}
```

### 3. Data Generation
```bash
# Ensure synthetic dataset exists
uv run python -m ingest.data_generator

# Verify users 0001, 0004, 0007, 0012, 0015 exist
uv run python -c "
import sqlite3
conn = sqlite3.connect('data/users.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT user_id, persona FROM users WHERE user_id IN (\"user_0001\", \"user_0004\", \"user_0007\", \"user_0012\", \"user_0015\")')
print(cursor.fetchall())
"
```

---

## Test Cases

### Test Case 1: Generate Video for user_0001

**Steps:**
1. Run recommendation generation:
```bash
uv run python -c "
from recommend.engine import generate_recommendations
import json
result = generate_recommendations('user_0001')
print(json.dumps(result, indent=2))
"
```

2. Check for video_url in output:
```bash
# Should see video_url field in recommendations
# Example output:
# {
#   "type": "education",
#   "title": "Understanding Credit Utilization",
#   "video_url": "https://sora.openai.com/v/abc123...",
#   "video_metadata": {
#     "duration": 8,
#     "resolution": "720p",
#     "generated_at": "2025-11-05T10:00:00Z"
#   }
# }
```

3. Verify trace JSON updated:
```bash
cat docs/traces/user_0001.json | jq '.video_generation_log'
```

4. Test video URL (if real SORA API):
```bash
curl -I [video_url]
# Should return 200 status
```

**Expected Results:**
- [ ] Video URL present in recommendation
- [ ] Duration: 5-10 seconds
- [ ] Resolution: 720p
- [ ] Generation time: <30 seconds
- [ ] Trace JSON includes video_generation_log
- [ ] Video URL returns 200 status

---

### Test Case 2: Generate Video for user_0004

**Steps:** (Repeat Test Case 1 with user_0004)

```bash
uv run python -c "
from recommend.engine import generate_recommendations
import json
result = generate_recommendations('user_0004')
recs = [r for r in result['recommendations'] if r.get('video_url')]
if recs:
    print('Video generated:', recs[0]['video_url'])
    print('Duration:', recs[0]['video_metadata']['duration'])
else:
    print('No video generated')
"
```

**Expected Results:**
- [ ] Video URL present
- [ ] Duration: 5-10s
- [ ] Resolution: 720p
- [ ] Generation time: <30s

---

### Test Case 3: Generate Video for user_0007

**Steps:** (Repeat with user_0007)

```bash
uv run python -c "
from recommend.engine import generate_recommendations
result = generate_recommendations('user_0007')
# Check video_url in result
"
```

**Expected Results:**
- [ ] Video URL present
- [ ] Duration: 5-10s
- [ ] Resolution: 720p
- [ ] Generation time: <30s

---

### Test Case 4: Generate Video for user_0012

**Steps:** (Repeat with user_0012)

**Expected Results:**
- [ ] Video URL present
- [ ] Duration: 5-10s
- [ ] Resolution: 720p
- [ ] Generation time: <30s

---

### Test Case 5: Generate Video for user_0015

**Steps:** (Repeat with user_0015)

**Expected Results:**
- [ ] Video URL present
- [ ] Duration: 5-10s
- [ ] Resolution: 720p
- [ ] Generation time: <30s

---

## Validation Checklist

### Functional Requirements
- [ ] All 5 users successfully generated videos
- [ ] All video URLs return 200 status (if real API)
- [ ] All videos are 720p resolution
- [ ] All videos are 5-10 seconds duration
- [ ] All generation times <30 seconds

### Trace JSON Validation
- [ ] All 5 trace files include `video_generation_log` section
- [ ] Each log entry includes:
  - `timestamp`
  - `topic` ("credit_utilization")
  - `title`
  - `status` ("success" or "failed")
  - `video_url` (if success)
  - `duration_seconds` (if success)
  - `resolution` (if success)
  - `error` (if failed)

### Error Handling
Test error scenarios:

1. **Invalid API Key:**
```bash
export SORA_API_KEY="invalid-key"
uv run python -c "from recommend.engine import generate_recommendations; generate_recommendations('user_0001')"
# Should gracefully degrade (no exception, video_error field set)
```

2. **API Disabled:**
```bash
export SORA_ENABLED=false
uv run python -c "from recommend.engine import generate_recommendations; generate_recommendations('user_0001')"
# Should generate recommendations without video_url
```

3. **Network Timeout:**
```bash
# Simulate by setting very short timeout in constants.py
# Verify retry logic activates (check logs)
```

---

## Test Results Template

### Summary Table

| User ID | Persona | Video URL | Duration | Resolution | Gen Time | Status |
|---------|---------|-----------|----------|------------|----------|--------|
| user_0001 | high_utilization | https://... | 8s | 720p | 14.2s | ✅ |
| user_0004 | high_utilization | https://... | 7s | 720p | 12.8s | ✅ |
| user_0007 | high_utilization | https://... | 8s | 720p | 15.1s | ✅ |
| user_0012 | high_utilization | https://... | 9s | 720p | 13.4s | ✅ |
| user_0015 | high_utilization | https://... | 8s | 720p | 14.7s | ✅ |

### Notes
- **Date Tested:** [YYYY-MM-DD]
- **Tester:** [Name]
- **SORA API Version:** [sora-1.0-turbo]
- **Issues Found:** [None | List issues]
- **Performance:** [Average generation time: XX.Xs]

---

## Troubleshooting

### Issue: "SORA API key required" ValueError

**Cause:** API key not set or empty
**Solution:**
```bash
export SORA_API_KEY="sk-your-key"
```

### Issue: "Failed to initialize SORA video generator" Warning

**Cause:** Invalid API key or network issue
**Solution:** Verify API key is correct, check network connectivity

### Issue: video_url is null in recommendations

**Cause:** Video generation failed (timeout, rate limit, API error)
**Solution:** Check `video_error` field, review logs, verify API access

### Issue: No credit_utilization recommendations for user

**Cause:** User's persona or signals don't trigger credit_utilization topic
**Solution:** Use different test user with high_utilization persona

---

## Next Steps

After successful POC testing:
1. Document results in `docs/video_test_results.md`
2. Update decision log with findings
3. Proceed to Chunk 2: Scale-out Infrastructure
4. Implement cache layer and background job queue

---

**Document Version:** 1.0
**Last Updated:** 2025-11-05
**Related Docs:**
- `docs/video_generation/CHUNK_1_POC.md`
- `docs/video_generation/ARCHITECTURE.md`
