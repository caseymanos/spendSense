# Educational Videos - Placeholder Notice

## Current Status

The YouTube video IDs in `seed_educational_videos.py` are **PLACEHOLDERS** using verified YouTube videos to demonstrate the video feature functionality.

**These are NOT actual financial education videos** - they're popular YouTube videos that:
- Have guaranteed thumbnail availability
- Work with the YouTube player
- Demonstrate the video card and modal player features

## How to Replace with Real Financial Education Videos

### Step 1: Find Videos on YouTube
Search YouTube for each topic:
- Credit utilization explained
- Debt avalanche vs snowball
- Emergency fund for irregular income
- Subscription audit tips
- Variable income budgeting
- High-yield savings accounts
- Zero-based budgeting
- SMART financial goals

### Step 2: Extract Video IDs
From a YouTube URL like: `https://www.youtube.com/watch?v=ABC123xyz`
The video ID is: `ABC123xyz`

### Step 3: Update the Seed Script
Edit `scripts/seed_educational_videos.py`:
1. Find the topic section (e.g., `# CREDIT UTILIZATION`)
2. Replace the `youtube_id` value with your real video ID
3. Update the `title`, `channel_name`, and `description` to match
4. Update `duration_seconds` (optional - get from YouTube)

### Step 4: Re-seed the Database
```bash
uv run python scripts/seed_educational_videos.py
```

## Recommended Financial Education Channels

- **Graham Stephan** - Personal finance, investing, real estate
- **The Financial Diet** - Budgeting, money management for millennials
- **Two Cents** (PBS) - Economics and personal finance
- **The Money Guy Show** - Financial planning and wealth building
- **YNAB** (You Need A Budget) - Budgeting methodology
- **Andrei Jikh** - Investing and credit cards
- **Minority Mindset** - Financial education and entrepreneurship

## Validation

After updating, verify thumbnails load:
```bash
# Test a video ID
curl -I https://img.youtube.com/vi/YOUR_VIDEO_ID/hqdefault.jpg

# Should return: HTTP/1.1 200 OK
```

## Current Placeholder Count

- **26 placeholder videos** across 8 financial topics
- All verified to have working thumbnails
- Ready to be replaced with curated financial education content
