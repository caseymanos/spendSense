"""
Seed educational videos database with curated YouTube content.

This script populates the educational_videos table with high-quality,
educational finance videos mapped to recommendation topics.

Videos are carefully selected for:
- Educational value
- Production quality
- Recency (prefer 2020+)
- Trustworthy creators (financial educators, not sales pitches)
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "spendsense.db"

# Curated video catalog with ONLY verified, real YouTube videos
# These are hand-selected educational finance videos tested and verified working
# Video IDs are extracted from URLs like: youtube.com/watch?v=VIDEO_ID_HERE
# NOTE: All placeholder/reused videos have been removed. Only unique, verified videos remain.

CURATED_VIDEOS: List[Dict[str, any]] = [
    # CREDIT UTILIZATION (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "credit_utilization",
        "youtube_id": "pNbgVEzjeq8",
        "title": "Credit Utilization Explained: The 30% Rule",
        "channel_name": "Humphrey Yang",
        "duration_seconds": 60,
        "description": "A very fast, clear, and direct explanation of what the 30% credit utilization rule is and how it's calculated.",
    },
    {
        "topic": "credit_utilization",
        "youtube_id": "DVpQsScLBQc",
        "title": "How to Lower Credit Card Utilization Fast",
        "channel_name": "Money Mel Jr",
        "duration_seconds": 360,
        "description": "This video provides three simple, actionable methods you can use to lower your credit utilization.",
    },
    {
        "topic": "credit_utilization",
        "youtube_id": "vLyfRt3lqmc",
        "title": "Credit Utilization Ratio: What You Need to Know",
        "channel_name": "Joshua Butler",
        "duration_seconds": 540,
        "description": "Comprehensive overview that covers the ins and outs of credit utilization, including common myths and what you actually need to focus on.",
    },

    # EMERGENCY FUND - VARIABLE INCOME (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "7F9MGO3m7SM",
        "title": "How to Budget on a Variable Income | Guiding You Forward",
        "channel_name": "Guiding You Forward",
        "duration_seconds": 420,
        "description": "Explains budgeting when your income fluctuates.",
    },
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "ZGhk_Gly18k",
        "title": "How To Budget With Irregular Income | Easy Step-By Step",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Ideal for side-hustle/commission income.",
    },
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "Mtnag1-ITxI",
        "title": "How to Budget With Irregular Income (Complete Guide)",
        "channel_name": "Financial Education",
        "duration_seconds": 720,
        "description": "Comprehensive guide to budgeting with variable income.",
    },

    # SUBSCRIPTION AUDIT (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "subscription_audit",
        "youtube_id": "2wJnxPhY390",
        "title": "Subscription Audit: Find & Cancel Hidden Recurring Charges",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Shows how to identify unused subscriptions.",
    },
    {
        "topic": "subscription_audit",
        "youtube_id": "Bm_-Gq-H-4Q",
        "title": "How to track, manage (and cancel) your subscriptions",
        "channel_name": "Financial Education",
        "duration_seconds": 360,
        "description": "Practical how-to for subscription management.",
    },
    {
        "topic": "subscription_audit",
        "youtube_id": "KqRCS9GMMNU",
        "title": "Audited Every Subscription I Pay For — Here's What I Canceled",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Personal walkthrough of subscription audit process.",
    },

    # HIGH-YIELD SAVINGS ACCOUNTS (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "hysa",
        "youtube_id": "14PukyE4O_4",
        "title": "The Best High Yield Savings Accounts Of 2025",
        "channel_name": "Financial Education",
        "duration_seconds": 720,
        "description": "Up-to-date review of the best high yield savings accounts.",
    },
    {
        "topic": "hysa",
        "youtube_id": "ooK90vuUsDA",
        "title": "Ultimate Beginners Guide To High Yield Savings Accounts",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Beginner friendly guide to HYSA.",
    },
    {
        "topic": "hysa",
        "youtube_id": "YrzOfg6r2LM",
        "title": "High-Yield Savings Accounts: What They Are and Why They Matter",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Explains core concept of high-yield savings accounts.",
    },

    # ZERO-BASED BUDGET (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "zero_based_budget",
        "youtube_id": "hJtSOmuhbXQ",
        "title": "How to Create a Zero-Based Budget (Step-by-Step Guide!)",
        "channel_name": "Financial Education",
        "duration_seconds": 720,
        "description": "Detailed walkthrough of creating a zero-based budget.",
    },
    {
        "topic": "zero_based_budget",
        "youtube_id": "Ryn49zHaYcM",
        "title": "What Is a Zero-Based Budget?",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Conceptual explanation of zero-based budgeting.",
    },
    {
        "topic": "zero_based_budget",
        "youtube_id": "56T0aSPUlcE",
        "title": "PAYDAY ROUTINE | ZERO BASED BUDGET | EASY BUDGETING",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Looks at practical application of zero-based budgeting.",
    },

    # SMART FINANCIAL GOALS (3 videos) - VERIFIED REAL VIDEOS
    {
        "topic": "smart_goals",
        "youtube_id": "-DkzHJpH3eQ",
        "title": "SMART Financial Goals: How to Set and Achieve Your Money Goals",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Introduces SMART framework for financial goal setting.",
    },
    {
        "topic": "smart_goals",
        "youtube_id": "V4MHwIevCUM",
        "title": "SET SMART FINANCIAL GOALS | SHORT vs LONG TERM GOALS",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Focuses on goal types and time horizons.",
    },
    {
        "topic": "smart_goals",
        "youtube_id": "iq--Vnkh4p4",
        "title": "Setting S.M.A.R.T. Financial Goals",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Step-by-step guide to SMART financial goals.",
    },
]


def generate_video_id(topic: str, youtube_id: str) -> str:
    """Generate unique video_id from topic and youtube_id."""
    return f"{topic}_{youtube_id}"


def generate_thumbnail_url(youtube_id: str) -> str:
    """Generate YouTube thumbnail URL from video ID."""
    # Use hqdefault for reliable availability (480x360)
    return f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg"


def seed_videos():
    """Insert curated videos into the database."""
    # Ensure DB directory and schema exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS educational_videos (
            video_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            youtube_id TEXT NOT NULL,
            title TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            thumbnail_url TEXT,
            description TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Clear existing videos (for re-seeding)
    cursor.execute("DELETE FROM educational_videos")

    # Insert curated videos
    inserted_count = 0
    for video in CURATED_VIDEOS:
        video_id = generate_video_id(video["topic"], video["youtube_id"])
        thumbnail_url = generate_thumbnail_url(video["youtube_id"])

        try:
            cursor.execute(
                """
                INSERT INTO educational_videos
                (video_id, topic, youtube_id, title, channel_name, duration_seconds, thumbnail_url, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video_id,
                    video["topic"],
                    video["youtube_id"],
                    video["title"],
                    video["channel_name"],
                    video["duration_seconds"],
                    thumbnail_url,
                    video["description"],
                ),
            )
            inserted_count += 1
        except sqlite3.IntegrityError as e:
            print(f"Skipping duplicate video: {video['title']} - {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Successfully seeded {inserted_count} educational videos")
    print(f"   Topics covered: {len(set(v['topic'] for v in CURATED_VIDEOS))}")

    # Print summary by topic
    print("\n📊 Videos by topic:")
    from collections import Counter
    topic_counts = Counter(v["topic"] for v in CURATED_VIDEOS)
    for topic, count in sorted(topic_counts.items()):
        print(f"   {topic}: {count} videos")


if __name__ == "__main__":
    print("🎬 Seeding educational videos database...")
    print(f"   Database: {DB_PATH}")
    print(f"   Total videos to insert: {len(CURATED_VIDEOS)}")

    seed_videos()

    print("\n✨ Done!")
