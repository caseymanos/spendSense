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
# NOTE: These YouTube video IDs are PLACEHOLDERS using popular videos to demonstrate functionality
# TODO: Replace with actual financial education videos by searching YouTube for each topic
# and extracting the video ID from URLs like: youtube.com/watch?v=VIDEO_ID_HERE

CURATED_VIDEOS: List[Dict[str, any]] = [
    # CREDIT UTILIZATION (3 videos) - PLACEHOLDER IDS - REPLACE WITH REAL FINANCE VIDEOS
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

    # EMERGENCY FUND - VARIABLE INCOME (3 videos) - PLACEHOLDER IDS
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "L_jWHffIx5E",  # PLACEHOLDER - Search: "emergency fund irregular income"
        "title": "Building an Emergency Fund with Irregular Income",
        "channel_name": "Financial Education",
        "duration_seconds": 531,
        "description": "Strategies for freelancers and gig workers to build emergency savings despite income fluctuations.",
    },
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "34Na4j8AVgA",  # PLACEHOLDER - Search: "emergency fund freelancers"
        "title": "Emergency Fund for Freelancers: How Much You Really Need",
        "channel_name": "Financial Education",
        "duration_seconds": 418,
        "description": "Guidance on calculating emergency fund size when income varies month to month.",
    },
    {
        "topic": "emergency_fund_variable_income",
        "youtube_id": "YQHsXMglC9A",  # PLACEHOLDER - Search: "budgeting irregular income"
        "title": "Variable Income Budget | How to Budget with Irregular Income",
        "channel_name": "Financial Education",
        "duration_seconds": 742,
        "description": "Complete system for budgeting and saving when income isn't consistent.",
    },

    # SUBSCRIPTION AUDIT (4 videos) - PLACEHOLDER IDS
    {
        "topic": "subscription_audit",
        "youtube_id": "3JZ_D3ELwOQ",  # PLACEHOLDER - Search: "subscription audit"
        "title": "How to Do a Subscription Audit and Save Money",
        "channel_name": "Financial Education",
        "duration_seconds": 367,
        "description": "Step-by-step process to identify, evaluate, and cancel unused subscription services.",
    },
    {
        "topic": "subscription_audit",
        "youtube_id": "hT_nvWreIhg",  # PLACEHOLDER - Search: "cancel subscriptions save money"
        "title": "I Cancelled All My Subscriptions and Saved $200/Month",
        "channel_name": "Financial Education",
        "duration_seconds": 512,
        "description": "Personal audit walkthrough showing how to identify subscription creep and take action.",
    },
    {
        "topic": "subscription_audit",
        "youtube_id": "KQ6zr6kCPj8",  # PLACEHOLDER - Search: "subscription spending"
        "title": "Subscription Spending is Out of Control: Here's How to Fix It",
        "channel_name": "Financial Education",
        "duration_seconds": 429,
        "description": "Analysis of subscription economics and practical tools for tracking recurring charges.",
    },
    {
        "topic": "subscription_audit",
        "youtube_id": "Ahg6qcgoay4",  # PLACEHOLDER - Search: "free alternatives subscriptions"
        "title": "Free Alternatives to Popular Paid Subscriptions",
        "channel_name": "Financial Education",
        "duration_seconds": 654,
        "description": "Comprehensive list of free alternatives to streaming, productivity, and software subscriptions.",
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

    # HIGH-YIELD SAVINGS ACCOUNTS (3 videos) - PLACEHOLDER IDS
    {
        "topic": "hysa",
        "youtube_id": "MtN1YnoL46Q",  # PLACEHOLDER - Search: "high yield savings account"
        "title": "High Yield Savings Accounts Explained (And the Best Ones)",
        "channel_name": "Financial Education",
        "duration_seconds": 625,
        "description": "Overview of HYSA benefits, FDIC insurance, and comparison of top online banks.",
    },
    {
        "topic": "hysa",
        "youtube_id": "QB7EpnGZxVA",  # PLACEHOLDER - Search: "why use high yield savings"
        "title": "Why You Should Move Your Money to a High-Yield Savings Account",
        "channel_name": "Financial Education",
        "duration_seconds": 443,
        "description": "Explanation of how HYSA rates compare to traditional banks and compound interest math.",
    },
    {
        "topic": "hysa",
        "youtube_id": "d0tU18Ybcvk",  # PLACEHOLDER - Search: "best savings accounts 2024"
        "title": "Best High Yield Savings Accounts 2024",
        "channel_name": "Financial Education",
        "duration_seconds": 537,
        "description": "Comparison of top HYSA options including rates, minimums, and transfer times.",
    },

    # ZERO-BASED BUDGET (3 videos) - PLACEHOLDER IDS
    {
        "topic": "zero_based_budget",
        "youtube_id": "RBumgq5yVrA",  # PLACEHOLDER - Search: "zero based budget explained"
        "title": "Zero-Based Budget Explained | Give Every Dollar a Job",
        "channel_name": "Financial Education",
        "duration_seconds": 412,
        "description": "Introduction to zero-based budgeting principles and how to get started.",
    },
    {
        "topic": "zero_based_budget",
        "youtube_id": "lCYz_zRC_E0",  # PLACEHOLDER - Search: "how to create zero based budget"
        "title": "How to Create a Zero Based Budget (Step-by-Step)",
        "channel_name": "Financial Education",
        "duration_seconds": 718,
        "description": "Detailed walkthrough of creating your first zero-based budget with examples.",
    },
    {
        "topic": "zero_based_budget",
        "youtube_id": "uelHwf8o7_U",  # PLACEHOLDER - Search: "zero based budgeting method"
        "title": "Zero-Based Budgeting: The YNAB Method",
        "channel_name": "Financial Education",
        "duration_seconds": 556,
        "description": "YNAB's approach to zero-based budgeting with four rules and practical implementation.",
    },

    # SMART FINANCIAL GOALS (3 videos) - PLACEHOLDER IDS
    {
        "topic": "smart_goals",
        "youtube_id": "B_obeR1OIm8",  # PLACEHOLDER - Search: "SMART financial goals"
        "title": "How to Set SMART Financial Goals That Actually Work",
        "channel_name": "Financial Education",
        "duration_seconds": 467,
        "description": "Applying SMART framework to savings, debt payoff, and investment goals.",
    },
    {
        "topic": "smart_goals",
        "youtube_id": "astISOttCQ0",  # PLACEHOLDER - Search: "setting financial goals"
        "title": "Setting Financial Goals: A Complete Guide",
        "channel_name": "Financial Education",
        "duration_seconds": 892,
        "description": "Comprehensive goal-setting framework with short-term and long-term planning strategies.",
    },
    {
        "topic": "smart_goals",
        "youtube_id": "videoseries",  # PLACEHOLDER - Search: "financial goal setting beginners"
        "title": "Financial Goal Setting for Beginners",
        "channel_name": "Financial Education",
        "duration_seconds": 521,
        "description": "Beginner-friendly guide to identifying priorities and creating achievable financial milestones.",
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
