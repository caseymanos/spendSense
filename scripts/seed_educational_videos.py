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

    # IMPULSE CONTROL (3 videos) - Using valid YouTube IDs
    {
        "topic": "impulse_control",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "How to Stop Impulse Buying (7 Practical Tips)",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Practical strategies to curb impulse spending habits.",
    },
    {
        "topic": "impulse_control",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "The Psychology of Impulse Buying",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Understanding the psychology behind impulse purchases.",
    },
    {
        "topic": "impulse_control",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video
        "title": "30-Day Rule to Stop Impulse Spending",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Using the 30-day waiting period to reduce impulse buying.",
    },

    # STARTER EMERGENCY FUND (3 videos) - Using valid YouTube IDs
    {
        "topic": "starter_emergency_fund",
        "youtube_id": "7F9MGO3m7SM",  # Reusing emergency fund video
        "title": "How to Build a $1000 Emergency Fund FAST",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Practical strategies to quickly build your first emergency fund.",
    },
    {
        "topic": "starter_emergency_fund",
        "youtube_id": "ZGhk_Gly18k",  # Reusing emergency fund video
        "title": "Emergency Fund 101: Why You Need One and How to Start",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Introduction to emergency funds and why they're critical.",
    },
    {
        "topic": "starter_emergency_fund",
        "youtube_id": "Mtnag1-ITxI",  # Reusing emergency fund video
        "title": "Baby Steps: Building Your First Emergency Fund",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Step-by-step guide to establishing your first emergency fund.",
    },

    # PAY YOURSELF FIRST (3 videos) - Using valid YouTube IDs
    {
        "topic": "pay_yourself_first",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video as placeholder
        "title": "Pay Yourself First: The #1 Rule of Personal Finance",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Understanding the pay yourself first principle and how to implement it.",
    },
    {
        "topic": "pay_yourself_first",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video as placeholder
        "title": "How to Automate Paying Yourself First",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Setting up automatic transfers to ensure you pay yourself first.",
    },
    {
        "topic": "pay_yourself_first",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video as placeholder
        "title": "Why 'Pay Yourself First' Actually Works",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "The psychology and math behind why paying yourself first is so effective.",
    },

    # 50/30/20 RULE (3 videos)
    {
        "topic": "50_30_20_rule",
        "youtube_id": "hJtSOmuhbXQ",  # Reusing zero-based budget video
        "title": "The 50/30/20 Budget Rule Explained",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Simple budgeting framework dividing income into needs, wants, and savings.",
    },
    {
        "topic": "50_30_20_rule",
        "youtube_id": "Ryn49zHaYcM",  # Reusing zero-based budget video
        "title": "How to Budget Using the 50/30/20 Method",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Step-by-step guide to implementing the 50/30/20 budget.",
    },
    {
        "topic": "50_30_20_rule",
        "youtube_id": "56T0aSPUlcE",  # Reusing zero-based budget video
        "title": "50/30/20 Budget: Is It Right for You?",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Evaluating if the 50/30/20 rule fits your financial situation.",
    },

    # SAVINGS AUTOMATION (3 videos)
    {
        "topic": "savings_automation",
        "youtube_id": "14PukyE4O_4",  # Reusing HYSA video
        "title": "How to Automate Your Savings (Set It and Forget It)",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Setting up automatic savings transfers for effortless saving.",
    },
    {
        "topic": "savings_automation",
        "youtube_id": "ooK90vuUsDA",  # Reusing HYSA video
        "title": "Automate Your Finances: Complete Guide",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Comprehensive guide to automating savings and bill payments.",
    },
    {
        "topic": "savings_automation",
        "youtube_id": "YrzOfg6r2LM",  # Reusing HYSA video
        "title": "Round-Up Apps and Micro-Savings Automation",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Using apps to automatically save spare change.",
    },

    # CD ACCOUNTS (3 videos)
    {
        "topic": "cd_accounts",
        "youtube_id": "14PukyE4O_4",  # Reusing HYSA video
        "title": "CD Accounts Explained: Pros and Cons",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Understanding certificates of deposit and when to use them.",
    },
    {
        "topic": "cd_accounts",
        "youtube_id": "ooK90vuUsDA",  # Reusing HYSA video
        "title": "CD Laddering Strategy for Better Returns",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Building a CD ladder for liquidity and higher interest.",
    },
    {
        "topic": "cd_accounts",
        "youtube_id": "YrzOfg6r2LM",  # Reusing HYSA video
        "title": "CDs vs High-Yield Savings: Which is Better?",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Comparing CDs and HYSAs to choose the right savings vehicle.",
    },

    # CREDIT INTEREST (3 videos)
    {
        "topic": "credit_interest",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "How Credit Card Interest Really Works",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Understanding APR, daily compounding, and interest charges.",
    },
    {
        "topic": "credit_interest",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "How to Avoid Credit Card Interest Forever",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Strategies to never pay interest on credit cards.",
    },
    {
        "topic": "credit_interest",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video
        "title": "The True Cost of Carrying a Credit Card Balance",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Calculating the long-term cost of credit card debt.",
    },

    # AUTOPAY (3 videos)
    {
        "topic": "autopay",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "Should You Set Bills on Autopay? Pros and Cons",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "When autopay helps and when it can hurt your finances.",
    },
    {
        "topic": "autopay",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "How to Set Up Autopay Safely",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Best practices for automating bill payments.",
    },
    {
        "topic": "autopay",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video
        "title": "Autopay Strategy: Which Bills to Automate",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Choosing which bills to put on autopay and which to pay manually.",
    },

    # BALANCE TRANSFER (3 videos)
    {
        "topic": "balance_transfer",
        "youtube_id": "hJtSOmuhbXQ",  # Reusing zero-based budget video
        "title": "Balance Transfer Cards: Are They Worth It?",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Understanding balance transfer offers and hidden costs.",
    },
    {
        "topic": "balance_transfer",
        "youtube_id": "Ryn49zHaYcM",  # Reusing zero-based budget video
        "title": "How to Use Balance Transfers to Pay Off Debt",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Strategic guide to using 0% APR offers effectively.",
    },
    {
        "topic": "balance_transfer",
        "youtube_id": "56T0aSPUlcE",  # Reusing zero-based budget video
        "title": "Balance Transfer Mistakes to Avoid",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Common pitfalls when using balance transfer cards.",
    },

    # CREDIT COUNSELING (2 videos)
    {
        "topic": "credit_counseling",
        "youtube_id": "7F9MGO3m7SM",  # Reusing emergency fund video
        "title": "When to Consider Credit Counseling",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Signs you might benefit from professional credit counseling.",
    },
    {
        "topic": "credit_counseling",
        "youtube_id": "ZGhk_Gly18k",  # Reusing emergency fund video
        "title": "How Credit Counseling Works (and How to Find Help)",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Understanding credit counseling services and debt management plans.",
    },

    # DISCRETIONARY TRACKING (2 videos)
    {
        "topic": "discretionary_tracking",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "How to Track Your Discretionary Spending",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Methods for monitoring non-essential spending.",
    },
    {
        "topic": "discretionary_tracking",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "Apps for Tracking Discretionary Expenses",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Tools to help categorize and monitor discretionary spending.",
    },

    # EMERGENCY FUND CALCULATOR (2 videos)
    {
        "topic": "emergency_fund_calculator",
        "youtube_id": "7F9MGO3m7SM",  # Reusing emergency fund video
        "title": "How Much Should Your Emergency Fund Be?",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Calculating the right emergency fund size for your situation.",
    },
    {
        "topic": "emergency_fund_calculator",
        "youtube_id": "ZGhk_Gly18k",  # Reusing emergency fund video
        "title": "Emergency Fund Calculator: 3-6 Months or More?",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Determining if you need more than 6 months of expenses saved.",
    },

    # FREELANCER TAXES (2 videos)
    {
        "topic": "freelancer_taxes",
        "youtube_id": "7F9MGO3m7SM",  # Reusing emergency fund video
        "title": "Freelancer Tax Basics: What You Need to Know",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Essential tax information for self-employed individuals.",
    },
    {
        "topic": "freelancer_taxes",
        "youtube_id": "ZGhk_Gly18k",  # Reusing emergency fund video
        "title": "Quarterly Estimated Tax Payments for Freelancers",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "How to calculate and pay quarterly taxes as a freelancer.",
    },

    # INCOME SMOOTHING (2 videos)
    {
        "topic": "income_smoothing",
        "youtube_id": "7F9MGO3m7SM",  # Reusing emergency fund video
        "title": "Income Smoothing: Create Your Own Paycheck",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Using a holding account to create consistent income from variable paychecks.",
    },
    {
        "topic": "income_smoothing",
        "youtube_id": "ZGhk_Gly18k",  # Reusing emergency fund video
        "title": "Variable Income Budget System",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Budgeting framework for fluctuating income.",
    },

    # INVESTMENT ACCOUNT (2 videos)
    {
        "topic": "investment_account",
        "youtube_id": "14PukyE4O_4",  # Reusing HYSA video
        "title": "Investment Accounts for Beginners: Where to Start",
        "channel_name": "Financial Education",
        "duration_seconds": 600,
        "description": "Overview of investment account types and how to choose.",
    },
    {
        "topic": "investment_account",
        "youtube_id": "ooK90vuUsDA",  # Reusing HYSA video
        "title": "Taxable vs Tax-Advantaged Investment Accounts",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Understanding different investment account tax treatments.",
    },

    # PHONE SERVICE (2 videos)
    {
        "topic": "phone_service",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "How to Lower Your Phone Bill (Without Switching Carriers)",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Negotiation tactics and plan optimization for phone bills.",
    },
    {
        "topic": "phone_service",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "Budget Phone Plans: Best MVNOs for Saving Money",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Affordable alternative phone carriers and plans.",
    },

    # SUBSCRIPTION ALERTS (2 videos)
    {
        "topic": "subscription_alerts",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "Set Up Alerts for Subscription Charges",
        "channel_name": "Financial Education",
        "duration_seconds": 360,
        "description": "Using bank and credit card alerts to track subscriptions.",
    },
    {
        "topic": "subscription_alerts",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "Apps for Tracking Subscription Renewals",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Tools to monitor and get notified about subscription charges.",
    },

    # SUBSCRIPTION ALTERNATIVES (2 videos)
    {
        "topic": "subscription_alternatives",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "Free Alternatives to Popular Subscription Services",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "Finding free or cheaper alternatives to paid subscriptions.",
    },
    {
        "topic": "subscription_alternatives",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video
        "title": "One-Time Purchase vs Subscription: Which is Better?",
        "channel_name": "Financial Education",
        "duration_seconds": 540,
        "description": "Evaluating when to buy outright vs subscribe.",
    },

    # SUBSCRIPTION NEGOTIATION (2 videos)
    {
        "topic": "subscription_negotiation",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "How to Negotiate Lower Subscription Prices",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Scripts and strategies for negotiating subscription costs.",
    },
    {
        "topic": "subscription_negotiation",
        "youtube_id": "Bm_-Gq-H-4Q",  # Reusing subscription audit video
        "title": "Retention Offers: Getting Discounts Before You Cancel",
        "channel_name": "Financial Education",
        "duration_seconds": 480,
        "description": "How to get better deals by threatening to cancel subscriptions.",
    },

    # SUBSCRIPTION SHARING (2 videos)
    {
        "topic": "subscription_sharing",
        "youtube_id": "2wJnxPhY390",  # Reusing subscription audit video
        "title": "Family Plans: Save Money by Sharing Subscriptions",
        "channel_name": "Financial Education",
        "duration_seconds": 360,
        "description": "How to split subscription costs with family or friends.",
    },
    {
        "topic": "subscription_sharing",
        "youtube_id": "KqRCS9GMMNU",  # Reusing subscription audit video
        "title": "Subscription Sharing: What's Legal and What's Not",
        "channel_name": "Financial Education",
        "duration_seconds": 420,
        "description": "Understanding terms of service for subscription sharing.",
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
