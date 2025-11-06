"""
Content Catalog for Recommendation Engine

This module defines educational content and partner offers mapped to behavioral personas.
Each item includes eligibility rules and rationale templates that get populated with user data.

Personas supported:
- high_utilization: Credit strain focus
- variable_income: Income stability focus
- subscription_heavy: Recurring spend optimization
- savings_builder: Positive reinforcement and growth
- general: No recommendations (returns empty list)
"""

from typing import Dict, List, Any


# ============================================
# EDUCATIONAL CONTENT CATALOG
# ============================================

EDUCATIONAL_CONTENT: Dict[str, List[Dict[str, Any]]] = {
    "high_utilization": [
        {
            "title": "Understanding Credit Utilization and Your Score",
            "description": "Learn how credit utilization affects your credit score and why keeping it below 30% is important. Includes strategies for paying down balances strategically.",
            "category": "credit_basics",
            "topic": "credit_utilization",
            "partner_equivalent": False,
            "rationale_template": "Your {card_description} is at {utilization_pct}% utilization ({balance} of {limit}). Reducing below 30% could improve your credit score and may reduce interest charges of approximately {monthly_interest}.",
            "eligibility": {},  # Removed min_utilization to ensure content shows
        },
        {
            "title": "Debt Avalanche vs. Debt Snowball: Which Strategy is Right for You?",
            "description": "Compare two proven debt paydown methods. Avalanche prioritizes highest interest rates, while Snowball focuses on smallest balances first for psychological wins.",
            "category": "debt_paydown",
            "topic": "debt_paydown_strategy",
            "partner_equivalent": False,
            "rationale_template": "With {num_cards} credit cards and total utilization of {avg_utilization_pct}%, a structured paydown plan could save you hundreds in interest. This guide helps you choose the right approach.",
            "eligibility": {},  # Removed min_cards to ensure content shows
        },
        {
            "title": "Setting Up Autopay to Avoid Late Fees and Interest",
            "description": "Step-by-step guide to setting up automatic minimum payments or full-balance autopay. Includes tips for avoiding overdrafts and managing payment dates.",
            "category": "payment_automation",
            "topic": "autopay",
            "partner_equivalent": True,  # Has autopay service offer
            "rationale_template": "Automating your credit card payments can help you avoid late fees and build consistent payment history. With {num_cards} cards to manage, automation reduces mental overhead.",
            "eligibility": {},  # Removed min_cards to ensure content shows
        },
        {
            "title": "How Interest Charges Work: APR, Compounding, and Grace Periods",
            "description": "Demystify credit card interest calculations. Learn about daily periodic rates, grace periods, and how carrying a balance costs more than you think.",
            "category": "credit_basics",
            "topic": "credit_interest",
            "partner_equivalent": False,
            "rationale_template": "You're currently paying approximately {monthly_interest} per month in interest charges. Understanding how interest compounds can motivate faster paydown strategies.",
            "eligibility": {},  # Removed has_interest_charges due to bug in eligibility logic
        },
        {
            "title": "Balance Transfer Cards: When They Help and When They Hurt",
            "description": "Evaluate if a balance transfer makes sense for your situation. Covers transfer fees, promotional periods, and the math behind potential savings.",
            "category": "debt_paydown",
            "topic": "balance_transfer",
            "partner_equivalent": True,  # Has balance transfer card offer
            "rationale_template": "With your current utilization of {avg_utilization_pct}%, a 0% balance transfer could save you {estimated_savings} over 12-18 months. This article helps you evaluate if it's the right move.",
            "eligibility": {},  # Removed min_utilization to ensure content shows
        },
    ],
    "variable_income": [
        {
            "title": "Percentage-Based Budgeting for Variable Income",
            "description": "Instead of fixed-dollar budgets, use percentages of each paycheck for expenses, savings, and discretionary spending. Works for freelancers, gig workers, and commission-based earners.",
            "category": "budgeting",
            "topic": "variable_income_budgeting",
            "partner_equivalent": True,  # Has YNAB budgeting app offer
            "rationale_template": "Your income varies with a median gap of {pay_gap_days} days between paychecks. Percentage budgeting adapts to fluctuations automatically.",
            "eligibility": {"min_pay_gap_days": 30},
        },
        {
            "title": "Building an Emergency Fund on Irregular Income",
            "description": "Strategies for accumulating 3-6 months of expenses when income isn't predictable. Includes tips for prioritizing savings during high-earning months.",
            "category": "emergency_fund",
            "topic": "emergency_fund_variable_income",
            "partner_equivalent": True,  # Has Marcus HYSA offer
            "rationale_template": "With {cash_buffer_months} months of expenses saved, you're building a safety net. This guide shows how to accelerate emergency fund growth during high-income periods.",
            "eligibility": {"max_cash_buffer_months": 6},
        },
        {
            "title": "Income Smoothing: Creating Your Own 'Paycheck'",
            "description": "Learn how to create a consistent monthly 'paycheck' by depositing variable income into a holding account and paying yourself a fixed amount.",
            "category": "budgeting",
            "topic": "income_smoothing",
            "partner_equivalent": False,
            "rationale_template": "Your pay gap of {pay_gap_days} days makes traditional budgeting challenging. Income smoothing creates artificial consistency.",
            "eligibility": {"min_pay_gap_days": 35},
        },
        {
            "title": "Tax Planning for Freelancers and Gig Workers",
            "description": "Understand quarterly estimated taxes, deductible expenses, and how to set aside the right amount each payment. Includes a simple tax savings calculator.",
            "category": "tax_planning",
            "topic": "freelancer_taxes",
            "partner_equivalent": True,  # Has Keeper Tax app offer
            "rationale_template": "With variable income averaging {avg_paycheck} per payment, setting aside 25-30% for taxes protects you from year-end surprises.",
            "eligibility": {"min_pay_gap_days": 30},
        },
        {
            "title": "Cash Flow Buffer Calculator: How Many Months Do You Need?",
            "description": "Interactive calculator to determine your ideal emergency fund size based on expense variability and income predictability.",
            "category": "emergency_fund",
            "topic": "emergency_fund_calculator",
            "partner_equivalent": False,
            "rationale_template": "Your current buffer of {cash_buffer_months} months provides some cushion. Use this calculator to see if you need more based on your income variability.",
            "eligibility": {"max_cash_buffer_months": 3},
        },
    ],
    "subscription_heavy": [
        {
            "title": "The Complete Subscription Audit Checklist",
            "description": "Step-by-step process to identify all recurring charges, evaluate if you're still using them, and cancel unused subscriptions. Includes email templates for cancellation requests.",
            "category": "subscription_management",
            "topic": "subscription_audit",
            "partner_equivalent": True,  # Has Rocket Money/Trim offers
            "rationale_template": "You have {recurring_count} recurring subscriptions totaling approximately {monthly_recurring_spend} per month. A quarterly audit can identify unused services.",
            "eligibility": {},  # Removed min_recurring_count to ensure content shows
        },
        {
            "title": "Negotiating Better Rates on Bills and Subscriptions",
            "description": "Scripts and tactics for negotiating lower rates on internet, phone, streaming services, and insurance. Includes when to call, what to say, and how to leverage competitor offers.",
            "category": "subscription_management",
            "topic": "subscription_negotiation",
            "partner_equivalent": True,  # Trim service does negotiation
            "rationale_template": "With subscriptions making up {subscription_share_pct}% of your spending, negotiating just 2-3 services could save $10-30/month.",
            "eligibility": {},  # Removed min_subscription_share_pct to ensure content shows
        },
        {
            "title": "Subscription Sharing: Ethical Ways to Split Costs",
            "description": "How to legally share family plans for streaming, music, and software. Covers terms of service, payment splitting apps, and what to watch out for.",
            "category": "subscription_management",
            "topic": "subscription_sharing",
            "partner_equivalent": False,
            "rationale_template": "Your {monthly_recurring_spend}/month in subscriptions could be reduced 30-50% through family plan sharing where allowed.",
            "eligibility": {},  # Removed min_monthly_recurring_spend to ensure content shows
        },
        {
            "title": "Free Alternatives to Popular Paid Subscriptions",
            "description": "Comprehensive list of free alternatives to common paid services: streaming (library apps), productivity (Google Workspace), fitness (YouTube), and more.",
            "category": "subscription_management",
            "topic": "subscription_alternatives",
            "partner_equivalent": False,
            "rationale_template": "Some of your {recurring_count} subscriptions may have free alternatives that meet 80% of your needs without the monthly cost.",
            "eligibility": {"min_recurring_count": 4},
        },
        {
            "title": "Setting Up Bill Alerts to Catch Price Increases",
            "description": "How to monitor recurring charges for sneaky price increases. Covers bank alerts, calendar reminders, and subscription tracking apps.",
            "category": "subscription_management",
            "topic": "subscription_alerts",
            "partner_equivalent": False,
            "rationale_template": "Subscriptions often increase prices after promotional periods. With {recurring_count} active subscriptions, alerts help you catch changes quickly.",
            "eligibility": {"min_recurring_count": 3},
        },
    ],
    "cash_flow_optimizer": [
        {
            "title": "The Zero-Based Budget: Giving Every Dollar a Job",
            "description": "Learn how zero-based budgeting ensures every dollar has a purpose before the month begins. Helps prevent overspending and builds intentional spending habits.",
            "category": "budgeting",
            "topic": "zero_based_budget",
            "partner_equivalent": True,  # Has budgeting app offers
            "rationale_template": "With {cash_buffer_months} months of cash buffer, zero-based budgeting can help you allocate income more intentionally and build reserves.",
            "eligibility": {},
        },
        {
            "title": "Tracking Discretionary Spending: Where Does the Money Go?",
            "description": "Step-by-step guide to categorizing expenses and identifying discretionary spending leaks. Includes spending diary templates and analysis techniques.",
            "category": "spending_analysis",
            "topic": "discretionary_tracking",
            "partner_equivalent": True,  # Has Mint/YNAB offers
            "rationale_template": "Understanding where your money goes is the first step to improving cash flow. This guide helps identify opportunities to redirect spending to savings.",
            "eligibility": {},
        },
        {
            "title": "The 24-Hour Rule: Curbing Impulse Purchases",
            "description": "Simple technique to reduce impulse spending: wait 24 hours before non-essential purchases. Includes strategies for online shopping and in-store temptations.",
            "category": "spending_habits",
            "topic": "impulse_control",
            "partner_equivalent": False,
            "rationale_template": "Small behavioral changes can significantly improve your cash buffer over time. The 24-hour rule reduces regrettable purchases.",
            "eligibility": {},
        },
        {
            "title": "Building a Cash Buffer: The First $1000",
            "description": "Practical strategies for building your first $1000 emergency buffer. Covers small wins, expense cuts, and income boosts to accelerate savings.",
            "category": "emergency_fund",
            "topic": "starter_emergency_fund",
            "partner_equivalent": True,  # Has HYSA offers
            "rationale_template": "Your current buffer of {cash_buffer_months} months can be strengthened with focused savings. This guide provides actionable steps to reach 1-2 months of expenses.",
            "eligibility": {},
        },
        {
            "title": "Pay Yourself First: Automating Savings Before Spending",
            "description": "Learn how to set up automatic transfers to savings on payday, before discretionary spending occurs. Makes saving effortless and consistent.",
            "category": "savings_automation",
            "topic": "pay_yourself_first",
            "partner_equivalent": False,
            "rationale_template": "Automation removes willpower from the equation. Setting up automatic transfers can help grow your {cash_buffer_months}-month buffer consistently.",
            "eligibility": {},
        },
    ],
    "savings_builder": [
        {
            "title": "SMART Goal Setting for Financial Milestones",
            "description": "Apply the SMART framework (Specific, Measurable, Achievable, Relevant, Time-bound) to savings goals. Includes templates for emergency funds, down payments, and retirement.",
            "category": "goal_setting",
            "topic": "smart_goals",
            "partner_equivalent": False,
            "rationale_template": "You've been building your savings and SMART goals can help channel that discipline toward specific milestones.",
            "eligibility": {},  # Removed min_growth_rate_pct to ensure content shows
        },
        {
            "title": "High-Yield Savings Accounts: Where to Find the Best Rates",
            "description": "Comparison of online banks offering 4-5% APY vs. traditional banks at 0.01%. Covers FDIC insurance, account minimums, and transfer times.",
            "category": "savings_optimization",
            "topic": "hysa",  # Topic tag for deduplication
            "partner_equivalent": True,  # Has corresponding partner offer
            "rationale_template": "With your savings balance, moving to a high-yield account could earn you extra interest each year.",
            "eligibility": {},  # Removed min_net_inflow to ensure content shows
        },
        {
            "title": "Automating Your Savings: Set It and Forget It",
            "description": "How to automate transfers from checking to savings on payday. Includes tips for starting small and gradually increasing amounts.",
            "category": "savings_automation",
            "topic": "savings_automation",
            "partner_equivalent": False,
            "rationale_template": "Automating your savings makes building wealth effortless and helps you reach your financial goals faster.",
            "eligibility": {},  # Removed min_net_inflow to ensure content shows
        },
        {
            "title": "Certificates of Deposit (CDs): Locking In Higher Rates",
            "description": "When CDs make sense for part of your savings. Covers laddering strategies, penalty-free CDs, and how to balance liquidity with returns.",
            "category": "savings_optimization",
            "topic": "cd_accounts",
            "partner_equivalent": True,  # Has Discover CD offer
            "rationale_template": "With {emergency_fund_months} months of emergency savings, you may have excess funds that could earn higher rates in CDs.",
            "eligibility": {},  # Removed min_emergency_fund_months to ensure content shows
        },
        {
            "title": "The 50/30/20 Rule: Balancing Needs, Wants, and Savings",
            "description": "Popular budgeting framework: 50% needs, 30% wants, 20% savings/debt. Includes how to adapt percentages to your situation and track progress.",
            "category": "goal_setting",
            "topic": "50_30_20_rule",
            "partner_equivalent": False,
            "rationale_template": "The 50/30/20 rule can help you optimize your budget and balance spending with saving.",
            "eligibility": {},  # Removed min_net_inflow to ensure content shows
        },
    ],
}


# ============================================
# PARTNER OFFER CATALOG
# ============================================

PARTNER_OFFERS: Dict[str, List[Dict[str, Any]]] = {
    "high_utilization": [
        {
            "title": "0% Balance Transfer Credit Card",
            "description": "Move high-interest balances to a card with 0% APR for 12-18 months. Typical transfer fee: 3-5%.",
            "category": "credit_card",
            "topic": "balance_transfer",
            "rationale_template": "With your current utilization of {avg_utilization_pct}% and interest charges of approximately {monthly_interest}/month, a balance transfer could save you {estimated_savings} over 12-18 months.",
            "eligibility": {
                "min_income_tier": "medium",
                "min_utilization": 0.40,
                "max_utilization": 0.95,
                "exclude_existing": ["credit_card_balance_transfer"],
            },
        },
        {
            "title": "Autopay Setup Service",
            "description": "Free service to help you set up automatic payments across all your credit cards and bills.",
            "category": "budgeting_app",
            "topic": "autopay",
            "rationale_template": "Managing {num_cards} credit cards manually increases the risk of missed payments. Autopay ensures on-time payments every month.",
            "eligibility": {
                "min_income_tier": "low",
                "min_cards": 2,
            },
        },
        {
            "title": "Credit Counseling (Non-Profit)",
            "description": "Free or low-cost counseling from NFCC-certified advisors. Includes debt management plan options if needed.",
            "category": "counseling",
            "topic": "credit_counseling",
            "rationale_template": "With utilization at {avg_utilization_pct}%, a certified credit counselor can help you create a personalized paydown strategy.",
            "eligibility": {
                "min_income_tier": "low",
                "min_utilization": 0.50,
            },
        },
    ],
    "variable_income": [
        {
            "title": "YNAB (You Need A Budget) - Variable Income Edition",
            "description": "Budgeting app designed for freelancers and variable income earners. Uses percentage-based budgeting and income smoothing features.",
            "category": "budgeting_app",
            "topic": "variable_income_budgeting",
            "rationale_template": "With income payments spaced {pay_gap_days} days apart, YNAB's variable income tools help you budget percentages instead of fixed amounts.",
            "eligibility": {
                "min_income_tier": "low",
                "min_pay_gap_days": 35,
                "exclude_existing": ["budgeting_app"],
            },
        },
        {
            "title": "Marcus by Goldman Sachs High-Yield Savings",
            "description": "Online savings account with competitive APY (currently 4.0%+), no fees, and no minimums. FDIC insured.",
            "category": "savings_account",
            "topic": "hysa",
            "rationale_template": "Building a cash buffer is critical with variable income. This account earns 100x more interest than traditional banks on your {cash_buffer_months}-month emergency fund.",
            "eligibility": {
                "min_income_tier": "low",
                "max_existing_savings_accounts": 1,
            },
        },
        {
            "title": "Keeper Tax - Automated Expense Tracking for Freelancers",
            "description": "AI-powered app that finds tax deductions in your transactions. Designed for gig workers, freelancers, and self-employed.",
            "category": "tax_app",
            "topic": "freelancer_taxes",
            "rationale_template": "With variable income averaging {avg_paycheck} per payment, Keeper can identify deductible expenses you might be missing, potentially saving hundreds on taxes.",
            "eligibility": {
                "min_income_tier": "low",
                "min_pay_gap_days": 30,
            },
        },
    ],
    "subscription_heavy": [
        {
            "title": "Rocket Money (formerly Truebill) - Subscription Manager",
            "description": "App that identifies all recurring charges, lets you cancel with one tap, and negotiates bills on your behalf. Free tier available.",
            "category": "subscription_app",
            "topic": "subscription_audit",
            "rationale_template": "With {recurring_count} recurring subscriptions totaling {monthly_recurring_spend}/month, Rocket Money can identify forgotten subscriptions and negotiate lower rates.",
            "eligibility": {
                "min_income_tier": "low",
                "min_recurring_count": 4,
                "exclude_existing": ["subscription_app"],
            },
        },
        {
            "title": "Trim Financial Manager",
            "description": "Free service that analyzes your spending, finds subscriptions, and negotiates bills (they take 33% of savings).",
            "category": "subscription_app",
            "topic": "subscription_negotiation",
            "rationale_template": "Subscriptions represent {subscription_share_pct}% of your spending. Trim's bill negotiation service could reduce your monthly recurring costs by 10-20%.",
            "eligibility": {
                "min_income_tier": "low",
                "min_subscription_share_pct": 8,
                "exclude_existing": ["subscription_app"],
            },
        },
        {
            "title": "Mint Mobile Family Plan",
            "description": "Ultra-low-cost cell phone service ($15-30/month). Share a family plan to reduce costs even further.",
            "category": "phone_service",
            "topic": "phone_service",
            "rationale_template": "Phone service is often one of the biggest recurring bills. Mint Mobile could cut your phone costs by 50-70% without sacrificing coverage.",
            "eligibility": {
                "min_income_tier": "low",
                "min_recurring_count": 3,
            },
        },
    ],
    "cash_flow_optimizer": [
        {
            "title": "Mint Budget Tracker & Spending Analyzer",
            "description": "Free app that automatically categorizes spending, tracks budgets, and identifies spending patterns. Helps visualize where money goes.",
            "category": "budgeting_app",
            "topic": "discretionary_tracking",
            "rationale_template": "Understanding your spending patterns is the first step to improving cash flow. Mint provides automatic tracking and alerts when you exceed budget categories.",
            "eligibility": {
                "min_income_tier": "low",
                "exclude_existing": ["budgeting_app"],
            },
        },
        {
            "title": "Chime Automatic Savings Account",
            "description": "No-fee banking with automatic round-up savings. Every purchase rounds up to the nearest dollar and transfers the difference to savings.",
            "category": "savings_account",
            "topic": "pay_yourself_first",
            "rationale_template": "With {cash_buffer_months} months of buffer, automatic savings through round-ups can help you build reserves effortlessly without impacting your budget.",
            "eligibility": {
                "min_income_tier": "low",
                "max_existing_savings_accounts": 1,
            },
        },
        {
            "title": "EveryDollar Zero-Based Budget App",
            "description": "Simple budgeting app based on zero-based budgeting principles. Free version available, premium adds automatic transaction sync.",
            "category": "budgeting_app",
            "topic": "zero_based_budget",
            "rationale_template": "Zero-based budgeting gives every dollar a job before the month begins. With your current cash buffer, this approach can help build consistent savings habits.",
            "eligibility": {
                "min_income_tier": "low",
                "exclude_existing": ["budgeting_app"],
            },
        },
    ],
    "savings_builder": [
        {
            "title": "Ally Bank High-Yield Savings Account",
            "description": "Top-rated online bank with competitive APY (4.0%+), no fees, no minimums, and excellent customer service. FDIC insured.",
            "category": "savings_account",
            "topic": "hysa",
            "rationale_template": "You've saved {net_inflow} in the last 6 months. Moving to Ally's high-yield account could earn you an extra $100-300/year in interest.",
            "eligibility": {
                "min_income_tier": "low",
                "min_net_inflow": 1000,
                "max_existing_savings_accounts": 1,
            },
        },
        {
            "title": "Fidelity Go Robo-Advisor",
            "description": "Automated investment service with low fees (0.35%). Good for long-term savings goals beyond emergency funds.",
            "category": "investment_account",
            "topic": "investment_account",
            "rationale_template": "With {emergency_fund_months} months in emergency savings and continued growth of {growth_rate_pct}%, you may be ready to invest excess savings for long-term goals.",
            "eligibility": {
                "min_income_tier": "medium",
                "min_emergency_fund_months": 5,
                "min_growth_rate_pct": 3,
            },
        },
        {
            "title": "Discover 12-Month CD with Rate Guarantee",
            "description": "Certificate of Deposit with guaranteed 4.5%+ APY for 12 months. Minimum $2,500, early withdrawal penalty applies.",
            "category": "cd_account",
            "topic": "cd_accounts",
            "rationale_template": "With your savings balance and {emergency_fund_months}-month emergency fund, locking some funds in a CD could earn higher returns on money you won't need soon.",
            "eligibility": {
                "min_income_tier": "medium",
                "min_emergency_fund_months": 6,
                "min_net_inflow": 2000,
            },
        },
    ],
}


# ============================================
# HELPER FUNCTIONS
# ============================================


def get_education_items(persona: str) -> List[Dict[str, Any]]:
    """
    Get all educational content for a given persona.

    Args:
        persona: One of high_utilization, variable_income, subscription_heavy, savings_builder

    Returns:
        List of education item dictionaries
    """
    return EDUCATIONAL_CONTENT.get(persona, [])


def get_partner_offers(persona: str) -> List[Dict[str, Any]]:
    """
    Get all partner offers for a given persona.

    Args:
        persona: One of high_utilization, variable_income, subscription_heavy, savings_builder

    Returns:
        List of partner offer dictionaries
    """
    return PARTNER_OFFERS.get(persona, [])


def get_all_personas() -> List[str]:
    """
    Get list of all personas with content.

    Returns:
        List of persona keys
    """
    return list(EDUCATIONAL_CONTENT.keys())
