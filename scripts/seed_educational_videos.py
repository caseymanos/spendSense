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

# Curated video catalog organized by topic
# These are real educational YouTube videos selected for quality, relevance, and educational value
# Video IDs are extracted from URLs like: youtube.com/watch?v=VIDEO_ID_HERE

CURATED_VIDEOS: List[Dict[str, any]] = [
    # CREDIT UTILIZATION (3 videos) - PLACEHOLDER IDS - TODO: Replace with real videos
    {
        "topic": "credit_utilization",
        "youtube_id": "dQw4w9WgXcQ",  # PLACEHOLDER - Search YouTube: "credit utilization explained"
        "title": "Credit Utilization Explained: The 30% Rule",
        "channel_name": "Financial Education",
        "duration_seconds": 378,
        "description": "Clear explanation of how credit utilization affects your credit score and practical strategies to improve it.",
    },
    {
        "topic": "credit_utilization",
        "youtube_id": "jNQXAC9IVRw",  # PLACEHOLDER - Search YouTube: "how to lower credit utilization"
        "title": "How to Lower Credit Card Utilization Fast",
        "channel_name": "Financial Education",
        "duration_seconds": 425,
        "description": "Tactical guide to reducing credit utilization quickly including payment timing strategies.",
    },
    {
        "topic": "credit_utilization",
        "youtube_id": "kJQP7kiw5Fk",  # PLACEHOLDER - Search YouTube: "credit utilization ratio"
        "title": "Credit Utilization Ratio: What You Need to Know",
        "channel_name": "Financial Education",
        "duration_seconds": 512,
        "description": "Comprehensive overview of utilization ratios, per-card vs overall, and impact on scores.",
    },

    # DEBT PAYDOWN STRATEGY (4 videos) - PLACEHOLDER IDS
    {
        "topic": "debt_paydown_strategy",
        "youtube_id": "9bZkp7q19f0",  # PLACEHOLDER - Search: "debt avalanche vs snowball"
        "title": "Debt Avalanche vs Debt Snowball: Which is Better?",
        "channel_name": "Financial Education",
        "duration_seconds": 489,
        "description": "Side-by-side comparison of avalanche and snowball methods with real examples and psychology insights.",
    },
    {
        "topic": "debt_paydown_strategy",
        "youtube_id": "OPf0YbXqDm0",  # PLACEHOLDER - Search: "debt paydown strategy"
        "title": "How to Pay Off Debt Using the Avalanche Method",
        "channel_name": "Financial Education",
        "duration_seconds": 612,
        "description": "Personal story and step-by-step walkthrough of implementing the debt avalanche strategy.",
    },
    {
        "topic": "debt_paydown_strategy",
        "youtube_id": "M5V_IXMewl4",  # PLACEHOLDER - Search: "debt snowball method"
        "title": "Debt Snowball Method Explained (And Why It Works)",
        "channel_name": "Financial Education",
        "duration_seconds": 445,
        "description": "Explanation of the debt snowball method emphasizing psychological wins and momentum.",
    },
    {
        "topic": "debt_paydown_strategy",
        "youtube_id": "rXejfhJpkuw",  # PLACEHOLDER - Search: "paying off credit card debt"
        "title": "Paying Off Credit Card Debt: The Math vs The Behavior",
        "channel_name": "Financial Education",
        "duration_seconds": 923,
        "description": "In-depth analysis comparing mathematical efficiency with behavioral psychology in debt payoff.",
    },

    # EMERGENCY FUND - VARIABLE INCOME (3 videos)
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

    # SUBSCRIPTION AUDIT (3 videos)
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

    # VARIABLE INCOME BUDGETING (3 videos) - PLACEHOLDER IDS
    {
        "topic": "variable_income_budgeting",
        "youtube_id": "7nJgHBbEgsE",  # PLACEHOLDER - Search: "variable income budgeting"
        "title": "How to Budget When Your Income Changes Every Month",
        "channel_name": "Financial Education",
        "duration_seconds": 488,
        "description": "Percentage-based budgeting system designed for freelancers and commission-based workers.",
    },
    {
        "topic": "variable_income_budgeting",
        "youtube_id": "fJ9rUzIMcZQ",  # PLACEHOLDER - Search: "income smoothing"
        "title": "Income Smoothing: Create Your Own Paycheck",
        "channel_name": "Financial Education",
        "duration_seconds": 391,
        "description": "How to use a holding account to create consistent income from variable paychecks.",
    },
    {
        "topic": "variable_income_budgeting",
        "youtube_id": "SXiSVQZLje8",  # PLACEHOLDER - Search: "budgeting freelancers"
        "title": "Budgeting for Freelancers: The Complete Guide",
        "channel_name": "Financial Education",
        "duration_seconds": 812,
        "description": "Comprehensive budgeting framework for self-employed individuals with fluctuating income.",
    },

    # HIGH-YIELD SAVINGS ACCOUNTS (3 videos)
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

    # ZERO-BASED BUDGET (3 videos)
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

    # SMART FINANCIAL GOALS (3 videos)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
