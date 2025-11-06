# Chunk 3: UX Integration + Quality, Ops, and Optimization (Weeks 5-6)

**Objective:** Frontend video player, fallbacks, analytics, cost governance, operator controls.

**Timeline:** Weeks 5-6 (12 business days)
**Scope:** Web components, mobile responsiveness, infographic fallback, budget controls, analytics, A/B testing, performance
**Dependencies:** Chunks 1-2 complete

---

## Success Criteria

- ✅ UI: Cache loads <2s; graceful fallback always available
- ✅ Mobile: iOS/Android playback verified
- ✅ Ops: Cost <$150/month; completion rate >70%
- ✅ Performance: Page load impact <500ms
- ✅ Analytics: Track impressions, play, 25/50/75/100% progress, complete

---

## Frontend Architecture

### VideoPlayer Component Design

**File:** `web/components/VideoPlayer.tsx`
**Type:** Controlled component with event tracking

```typescript
'use client'

import React, { useRef, useState, useEffect } from 'react'
import { Loader2 } from 'lucide-react'

interface VideoPlayerProps {
  videoUrl?: string
  thumbnailUrl?: string
  title: string
  onPlay?: () => void
  onProgress?: (progress: number) => void
  onComplete?: () => void
  onError?: (error: Error) => void
}

enum LoadingState {
  Idle = 'idle',
  Loading = 'loading',
  Ready = 'ready',
  Error = 'error'
}

export function VideoPlayer({
  videoUrl,
  thumbnailUrl,
  title,
  onPlay,
  onProgress,
  onComplete,
  onError
}: VideoPlayerProps) {
  const [loadingState, setLoadingState] = useState<LoadingState>(LoadingState.Idle)
  const [progress, setProgress] = useState(0)
  const videoRef = useRef<HTMLVideoElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  // Lazy loading with Intersection Observer
  useEffect(() => {
    if (!containerRef.current || !videoUrl) return
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setLoadingState(LoadingState.Loading)
            observer.disconnect()
          }
        })
      },
      { rootMargin: '50px', threshold: 0.1 }
    )
    
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [videoUrl])
  
  // Video event listeners
  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    
    const handlePlay = () => {
      onPlay?.()
    }
    
    const handleTimeUpdate = () => {
      const percent = (video.currentTime / video.duration) * 100
      setProgress(percent)
      onProgress?.(percent)
    }
    
    const handleEnded = () => {
      onComplete?.()
    }
    
    const handleError = (e: Event) => {
      setLoadingState(LoadingState.Error)
      onError?.(new Error('Video failed to load'))
    }
    
    const handleLoadedData = () => {
      setLoadingState(LoadingState.Ready)
    }
    
    video.addEventListener('play', handlePlay)
    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('ended', handleEnded)
    video.addEventListener('error', handleError)
    video.addEventListener('loadeddata', handleLoadedData)
    
    return () => {
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('ended', handleEnded)
      video.removeEventListener('error', handleError)
      video.removeEventListener('loadeddata', handleLoadedData)
    }
  }, [onPlay, onProgress, onComplete, onError])
  
  if (!videoUrl) return null
  if (loadingState === LoadingState.Error) return null
  
  return (
    <div ref={containerRef} className="relative w-full aspect-video">
      {loadingState === LoadingState.Loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      )}
      {loadingState !== LoadingState.Idle && (
        <video
          ref={videoRef}
          src={videoUrl}
          poster={thumbnailUrl}
          controls
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          className="w-full rounded-lg"
          aria-label={title}
        />
      )}
    </div>
  )
}
```

---

### RecommendationCard Enhancement

**File:** `web/components/RecommendationCard.tsx`

```typescript
'use client'

import React from 'react'
import type { Recommendation } from '../lib/types'
import { Card, CardContent } from './ui/card'
import { VideoPlayer } from './VideoPlayer'
import { trackVideoEvent } from '../lib/analytics'

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  const handleVideoPlay = () => {
    trackVideoEvent({
      event_type: 'play',
      recommendation_id: rec.recommendation_id,
      video_url: rec.video_url!,
      timestamp: new Date().toISOString()
    })
  }
  
  const handleVideoProgress = (progress: number) => {
    // Track 25/50/75/100% markers
    const markers = [25, 50, 75, 100]
    markers.forEach(marker => {
      if (progress >= marker && !sessionStorage.getItem(`${rec.recommendation_id}_${marker}`)) {
        sessionStorage.setItem(`${rec.recommendation_id}_${marker}`, 'true')
        trackVideoEvent({
          event_type: 'progress',
          recommendation_id: rec.recommendation_id,
          video_url: rec.video_url!,
          progress_percent: marker,
          timestamp: new Date().toISOString()
        })
      }
    })
  }
  
  const handleVideoComplete = () => {
    trackVideoEvent({
      event_type: 'complete',
      recommendation_id: rec.recommendation_id,
      video_url: rec.video_url!,
      timestamp: new Date().toISOString()
    })
  }
  
  return (
    <Card className="mt-3">
      <CardContent className="py-4">
        {/* Video or Infographic */}
        {rec.video_url && rec.video_status === 'ready' && (
          <VideoPlayer
            videoUrl={rec.video_url}
            thumbnailUrl={rec.thumbnail_url}
            title={rec.title}
            onPlay={handleVideoPlay}
            onProgress={handleVideoProgress}
            onComplete={handleVideoComplete}
          />
        )}
        
        {rec.infographic_url && !rec.video_url && (
          <img
            src={rec.infographic_url}
            alt={rec.title}
            className="w-full rounded-lg mb-3"
          />
        )}
        
        {/* Text Content */}
        <div className="font-semibold">{rec.title}</div>
        <div className="mt-1 text-sm text-muted-foreground">{rec.rationale}</div>
        
        {/* Loading State */}
        {rec.video_status === 'loading' && (
          <div className="mt-2 text-xs text-muted-foreground">
            Video generating... ETA 2 minutes
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

---

### Type System Updates

**File:** `web/lib/types.ts`

```typescript
export type Recommendation = {
  recommendation_id: string
  type: 'education' | 'partner_offer'
  title: string
  rationale: string
  disclaimer: string
  
  // NEW: Video/media fields
  video_url?: string | null
  thumbnail_url?: string | null
  infographic_url?: string | null
  video_status?: 'loading' | 'ready' | 'failed' | 'not_requested'
  video_generation_cost?: number
  video_cached?: boolean
}
```

---

## Analytics Integration

### Event Tracking

**File:** `web/lib/analytics.ts`

```typescript
interface VideoAnalyticsEvent {
  event_type: 'impression' | 'play' | 'pause' | 'progress' | 'complete' | 'error'
  recommendation_id: string
  video_url: string
  timestamp: string
  progress_percent?: number
  error_code?: string
  error_message?: string
}

export function trackVideoEvent(event: VideoAnalyticsEvent): void {
  // Send to backend
  fetch('/api/analytics/video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event)
  }).catch(err => {
    // Fail silently - don't break UX
    console.warn('Analytics tracking failed:', err)
  })
}
```

---

### Backend Analytics Endpoint

**File:** `api/main.py`

```python
from pydantic import BaseModel

class VideoAnalyticsEvent(BaseModel):
    event_type: str
    recommendation_id: str
    video_url: str
    timestamp: str
    progress_percent: Optional[int] = None

@app.post("/api/analytics/video")
async def track_video_event(event: VideoAnalyticsEvent):
    """Append video analytics to user's trace JSON"""
    # Parse user_id from recommendation_id
    user_id = event.recommendation_id.split('_')[0]
    trace_file = Path(f"docs/traces/{user_id}.json")
    
    with open(trace_file, 'r+') as f:
        trace_data = json.load(f)
        
        if 'video_analytics' not in trace_data:
            trace_data['video_analytics'] = []
        
        trace_data['video_analytics'].append(event.dict())
        
        f.seek(0)
        json.dump(trace_data, f, indent=2)
        f.truncate()
    
    return {"status": "recorded"}
```

---

## Cost Governance

### Daily Budget Cap Enforcement

**File:** `api/services/cost_management.py`

```python
from datetime import date
from pathlib import Path
import json

COST_DB_PATH = Path("data/video_costs.json")

class CostTracker:
    def __init__(self, daily_budget: float = 5.00):
        self.daily_budget = daily_budget
        self.cost_db = self._load_cost_db()
    
    def can_afford_video(self, estimated_cost: float = 0.05) -> bool:
        """Check if we can afford another video today"""
        today = str(date.today())
        today_spend = self.cost_db.get(today, {}).get('total_cost', 0.0)
        
        return (today_spend + estimated_cost) <= self.daily_budget
    
    def record_video_cost(
        self, 
        recommendation_id: str, 
        cost: float,
        operator_override: bool = False
    ) -> None:
        """Record video generation cost"""
        today = str(date.today())
        
        if today not in self.cost_db:
            self.cost_db[today] = {
                'total_cost': 0.0,
                'videos_generated': 0,
                'operator_overrides': 0,
                'details': []
            }
        
        self.cost_db[today]['total_cost'] += cost
        self.cost_db[today]['videos_generated'] += 1
        
        if operator_override:
            self.cost_db[today]['operator_overrides'] += 1
        
        self.cost_db[today]['details'].append({
            'timestamp': datetime.now().isoformat(),
            'recommendation_id': recommendation_id,
            'cost': cost,
            'operator_override': operator_override
        })
        
        self._save_cost_db()
```

---

## Infographic Fallback Generator

**File:** `recommend/infographic_generator.py`

```python
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

def generate_static_infographic(recommendation: Dict[str, Any]) -> bytes:
    """
    Generate static SVG infographic as fallback.
    
    Uses template SVGs with dynamic data overlays.
    """
    template_name = recommendation.get('topic', 'default')
    template_path = Path(f"recommend/templates/{template_name}.svg")
    
    if not template_path.exists():
        # Fallback to text-only image
        return generate_text_card(
            recommendation['title'],
            recommendation['rationale']
        )
    
    # Read SVG template
    with open(template_path, 'r') as f:
        svg_content = f.read()
    
    # Inject dynamic data
    svg_content = svg_content.replace(
        '{utilization_pct}',
        str(int(recommendation.get('user_context', {}).get('credit_max_util_pct', 50)))
    )
    
    return svg_content.encode('utf-8')

def generate_text_card(title: str, description: str) -> bytes:
    """Last-resort fallback: simple text card"""
    img = Image.new('RGB', (1280, 720), color='#f3f4f6')
    draw = ImageDraw.Draw(img)
    
    # Draw title
    font_title = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 48)
    draw.text((100, 250), title, fill='#111827', font=font_title)
    
    # Draw description
    font_desc = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
    draw.text((100, 350), description[:100], fill='#6b7280', font=font_desc)
    
    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
```

---

## Video Quality Validation

**File:** `recommend/video_validator.py`

```python
import subprocess
import json
from pathlib import Path

class VideoValidator:
    MIN_RESOLUTION = (1280, 720)  # 720p
    MIN_DURATION = 10
    MAX_DURATION = 90
    
    def validate_video(self, video_path: Path) -> Dict[str, Any]:
        """Run validation checks on video file"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        if not video_path.exists():
            result["valid"] = False
            result["errors"].append("File not found")
            return result
        
        # Get metadata with ffprobe
        try:
            probe_result = subprocess.run([
                'ffprobe',
                '-v', 'error',
                '-show_format',
                '-show_streams',
                '-of', 'json',
                str(video_path)
            ], capture_output=True, text=True, check=True)
            
            metadata = json.loads(probe_result.stdout)
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"ffprobe failed: {e}")
            return result
        
        # Extract video stream
        video_stream = next((s for s in metadata.get('streams', []) if s['codec_type'] == 'video'), None)
        if not video_stream:
            result["valid"] = False
            result["errors"].append("No video stream found")
            return result
        
        # Check resolution
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        result["metadata"]["resolution"] = f"{width}x{height}"
        
        if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
            result["errors"].append(f"Resolution {width}x{height} below minimum {self.MIN_RESOLUTION}")
            result["valid"] = False
        
        # Check duration
        duration = float(metadata.get('format', {}).get('duration', 0))
        result["metadata"]["duration"] = duration
        
        if duration < self.MIN_DURATION:
            result["errors"].append(f"Duration {duration}s below minimum {self.MIN_DURATION}s")
            result["valid"] = False
        
        return result
```

---

## A/B Testing Harness

**File:** `api/services/ab_testing.py`

```python
from enum import Enum
import hashlib

class ExperimentVariant(Enum):
    CONTROL = "control"  # Text-only
    VIDEO = "video"      # Video-enhanced

class ABTestingService:
    def get_variant(self, user_id: str, experiment_name: str = "video_engagement") -> ExperimentVariant:
        """Get experiment variant for user (deterministic)"""
        bucket = int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % 100
        
        # 50/50 split
        if bucket < 50:
            return ExperimentVariant.VIDEO
        else:
            return ExperimentVariant.CONTROL
    
    def record_outcome(self, user_id: str, experiment_name: str, outcome: str, value: Optional[float] = None):
        """Record experiment outcome to trace JSON"""
        variant = self.get_variant(user_id, experiment_name)
        
        trace_file = Path(f"docs/traces/{user_id}.json")
        with open(trace_file, 'r+') as f:
            trace_data = json.load(f)
            
            if 'experiment_outcomes' not in trace_data:
                trace_data['experiment_outcomes'] = []
            
            trace_data['experiment_outcomes'].append({
                'timestamp': datetime.now().isoformat(),
                'experiment': experiment_name,
                'variant': variant.value,
                'outcome': outcome,
                'value': value
            })
            
            f.seek(0)
            json.dump(trace_data, f, indent=2)
            f.truncate()
```

---

## Operator Dashboard Integration

**File:** `ui/app_operator_nicegui.py`

Add 9th tab: **Video & Cost Management**

```python
@ui.refreshable
def render_video_cost_management_tab():
    """Render Video & Cost Management tab"""
    cost_tracker = CostTracker()
    summary = cost_tracker.get_today_summary()
    
    ui.label("Video Generation & Cost Management").classes("text-2xl font-bold mb-4")
    
    # Today's summary
    with ui.card().classes("w-full p-4 mb-4"):
        ui.label("Today's Summary").classes("text-lg font-bold mb-2")
        
        with ui.row().classes("gap-4"):
            # Total spend
            with ui.column():
                ui.label("Total Spend").classes("text-sm text-gray-600")
                spend_color = "red" if summary['total_cost'] > cost_tracker.daily_budget else "green"
                ui.label(f"${summary['total_cost']:.2f}").classes(f"text-2xl font-bold text-{spend_color}-600")
            
            # Budget remaining
            remaining = cost_tracker.daily_budget - summary['total_cost']
            with ui.column():
                ui.label("Remaining Budget").classes("text-sm text-gray-600")
                ui.label(f"${remaining:.2f}").classes("text-2xl font-bold")
            
            # Videos generated
            with ui.column():
                ui.label("Videos Generated").classes("text-sm text-gray-600")
                ui.label(str(summary['videos_generated'])).classes("text-2xl font-bold")
```

---

## Mobile Testing Checklist

| Feature | iOS Safari | Android Chrome | Desktop Chrome |
|---------|-----------|---------------|----------------|
| Video playback | ✅ | ✅ | ✅ |
| Thumbnail loading | ✅ | ✅ | ✅ |
| Touch controls | ✅ | ✅ | N/A |
| Landscape mode | ✅ | ✅ | N/A |
| Slow 3G | ⚠️ Fallback | ⚠️ Fallback | N/A |

**Test Devices:**
- iPhone 13 (iOS 15+)
- Pixel 6 (Android 11+)
- iPad Air 4 (iPadOS 15+)

---

## Performance Optimization

### Lazy Loading (Intersection Observer)

```typescript
useEffect(() => {
  if (!containerRef.current || !videoUrl) return
  
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setLoadingState(LoadingState.Loading)
          observer.disconnect()
        }
      })
    },
    { rootMargin: '50px', threshold: 0.1 }
  )
  
  observer.observe(containerRef.current)
  return () => observer.disconnect()
}, [videoUrl])
```

### Thumbnail Generation

**File:** `recommend/thumbnail_generator.py`

```python
import subprocess
from pathlib import Path

def generate_video_thumbnail(
    video_path: Path,
    timestamp: float = 1.0,
    size: tuple = (640, 360)
) -> Path:
    """Generate thumbnail from video using ffmpeg"""
    thumbnail_path = Path(f"data/thumbnails/{video_path.stem}_thumb.jpg")
    
    if thumbnail_path.exists():
        return thumbnail_path
    
    subprocess.run([
        'ffmpeg',
        '-i', str(video_path),
        '-ss', str(timestamp),
        '-vframes', '1',
        '-vf', f'scale={size[0]}:{size[1]}',
        str(thumbnail_path)
    ], check=True, capture_output=True)
    
    return thumbnail_path
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 5, Days 1-2)
- [ ] Update TypeScript types (`web/lib/types.ts`)
- [ ] Create VideoPlayer component
- [ ] Add video validation utility
- [ ] Update RecommendationCard
- [ ] Test with mock video URLs

### Phase 2: Fallback System (Week 5, Days 3-4)
- [ ] Create infographic generator
- [ ] Design 3 SVG templates
- [ ] Add decision tree logic
- [ ] Test fallback cascade

### Phase 3: Analytics (Week 6, Days 1-2)
- [ ] Create analytics library
- [ ] Add video event listeners
- [ ] Create analytics endpoint
- [ ] Update trace JSON schema

### Phase 4: Cost Governance (Week 6, Days 3-4)
- [ ] Create cost tracker
- [ ] Add budget checks
- [ ] Add Video & Costs tab
- [ ] Test budget enforcement

### Phase 5: Quality & Optimization (Week 6, Days 5-6)
- [ ] Add lazy loading
- [ ] Create thumbnail generator
- [ ] Add quality validation
- [ ] Optimize bundle size

### Phase 6: Final Integration (Week 6, Day 7)
- [ ] A/B testing service
- [ ] Experiment results dashboard
- [ ] Mobile testing
- [ ] Documentation

---

## Files to Create

1. `web/components/VideoPlayer.tsx` (~250 lines)
2. `web/lib/analytics.ts` (~150 lines)
3. `recommend/infographic_generator.py` (~300 lines)
4. `recommend/thumbnail_generator.py` (~100 lines)
5. `recommend/video_validator.py` (~150 lines)
6. `api/services/cost_management.py` (~200 lines)
7. `api/services/ab_testing.py` (~150 lines)
8. `recommend/templates/*.svg` (3 SVG templates)
9. `data/experiments.json` (config)

**Total Code:** ~2,420 lines

---

**Completion:** All 3 chunks complete! Ready for 6-week implementation.
