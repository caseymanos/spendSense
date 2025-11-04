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
            "rationale_template": "Your {card_description} is at {utilization_pct}% utilization ({balance} of {limit}). Reducing below 30% could improve your credit score and may reduce interest charges of approximately {monthly_interest}.",
            "eligibility": {"min_utilization": 0.30},
        },
        {
            "title": "Debt Avalanche vs. Debt Snowball: Which Strategy is Right for You?",
            "description": "Compare two proven debt paydown methods. Avalanche prioritizes highest interest rates, while Snowball focuses on smallest balances first for psychological wins.",
            "category": "debt_paydown",
            "rationale_template": "With {num_cards} credit cards and total utilization of {avg_utilization_pct}%, a structured paydown plan could save you hundreds in interest. This guide helps you choose the right approach.",
            "eligibility": {"min_cards": 2},
        },
        {
            "title": "Setting Up Autopay to Avoid Late Fees and Interest",
            "description": "Step-by-step guide to setting up automatic minimum payments or full-balance autopay. Includes tips for avoiding overdrafts and managing payment dates.",
            "category": "payment_automation",
            "rationale_template": "Automating your credit card payments can help you avoid late fees and build consistent payment history. With {num_cards} cards to manage, automation reduces mental overhead.",
            "eligibility": {"min_cards": 1},
        },
        {
            "title": "How Interest Charges Work: APR, Compounding, and Grace Periods",
            "description": "Demystify credit card interest calculations. Learn about daily periodic rates, grace periods, and how carrying a balance costs more than you think.",
            "category": "credit_basics",
            "rationale_template": "You're currently paying approximately {monthly_interest} per month in interest charges. Understanding how interest compounds can motivate faster paydown strategies.",
            "eligibility": {"has_interest_charges": True},
        },
        {
            "title": "Balance Transfer Cards: When They Help and When They Hurt",
            "description": "Evaluate if a balance transfer makes sense for your situation. Covers transfer fees, promotional periods, and the math behind potential savings.",
            "category": "debt_paydown",
            "rationale_template": "With your current utilization of {avg_utilization_pct}%, a 0% balance transfer could save you {estimated_savings} over 12-18 months. This article helps you evaluate if it's the right move.",
            "eligibility": {"min_utilization": 0.40},
        },
    ],
    "variable_income": [
        {
            "title": "Percentage-Based Budgeting for Variable Income",
            "description": "Instead of fixed-dollar budgets, use percentages of each paycheck for expenses, savings, and discretionary spending. Works for freelancers, gig workers, and commission-based earners.",
            "category": "budgeting",
            "rationale_template": "Your income varies with a median gap of {pay_gap_days} days between paychecks. Percentage budgeting adapts to fluctuations automatically.",
            "eligibility": {"min_pay_gap_days": 30},
        },
        {
            "title": "Building an Emergency Fund on Irregular Income",
            "description": "Strategies for accumulating 3-6 months of expenses when income isn't predictable. Includes tips for prioritizing savings during high-earning months.",
            "category": "emergency_fund",
            "rationale_template": "With {cash_buffer_months} months of expenses saved, you're building a safety net. This guide shows how to accelerate emergency fund growth during high-income periods.",
            "eligibility": {"max_cash_buffer_months": 6},
        },
        {
            "title": "Income Smoothing: Creating Your Own 'Paycheck'",
            "description": "Learn how to create a consistent monthly 'paycheck' by depositing variable income into a holding account and paying yourself a fixed amount.",
            "category": "budgeting",
            "rationale_template": "Your pay gap of {pay_gap_days} days makes traditional budgeting challenging. Income smoothing creates artificial consistency.",
            "eligibility": {"min_pay_gap_days": 35},
        },
        {
            "title": "Tax Planning for Freelancers and Gig Workers",
            "description": "Understand quarterly estimated taxes, deductible expenses, and how to set aside the right amount each payment. Includes a simple tax savings calculator.",
            "category": "tax_planning",
            "rationale_template": "With variable income averaging {avg_paycheck} per payment, setting aside 25-30% for taxes protects you from year-end surprises.",
            "eligibility": {"min_pay_gap_days": 30},
        },
        {
            "title": "Cash Flow Buffer Calculator: How Many Months Do You Need?",
            "description": "Interactive calculator to determine your ideal emergency fund size based on expense variability and income predictability.",
            "category": "emergency_fund",
            "rationale_template": "Your current buffer of {cash_buffer_months} months provides some cushion. Use this calculator to see if you need more based on your income variability.",
            "eligibility": {"max_cash_buffer_months": 3},
        },
    ],
    "subscription_heavy": [
        {
            "title": "The Complete Subscription Audit Checklist",
            "description": "Step-by-step process to identify all recurring charges, evaluate if you're still using them, and cancel unused subscriptions. Includes email templates for cancellation requests.",
            "category": "subscription_management",
            "rationale_template": "You have {recurring_count} recurring subscriptions totaling approximately {monthly_recurring_spend} per month. A quarterly audit can identify unused services.",
            "eligibility": {"min_recurring_count": 3},
        },
        {
            "title": "Negotiating Better Rates on Bills and Subscriptions",
            "description": "Scripts and tactics for negotiating lower rates on internet, phone, streaming services, and insurance. Includes when to call, what to say, and how to leverage competitor offers.",
            "category": "subscription_management",
            "rationale_template": "With subscriptions making up {subscription_share_pct}% of your spending, negotiating just 2-3 services could save $10-30/month.",
            "eligibility": {"min_subscription_share_pct": 5},
        },
        {
            "title": "Subscription Sharing: Ethical Ways to Split Costs",
            "description": "How to legally share family plans for streaming, music, and software. Covers terms of service, payment splitting apps, and what to watch out for.",
            "category": "subscription_management",
            "rationale_template": "Your {monthly_recurring_spend}/month in subscriptions could be reduced 30-50% through family plan sharing where allowed.",
            "eligibility": {"min_monthly_recurring_spend": 40},
        },
        {
            "title": "Free Alternatives to Popular Paid Subscriptions",
            "description": "Comprehensive list of free alternatives to common paid services: streaming (library apps), productivity (Google Workspace), fitness (YouTube), and more.",
            "category": "subscription_management",
            "rationale_template": "Some of your {recurring_count} subscriptions may have free alternatives that meet 80% of your needs without the monthly cost.",
            "eligibility": {"min_recurring_count": 4},
        },
        {
            "title": "Setting Up Bill Alerts to Catch Price Increases",
            "description": "How to monitor recurring charges for sneaky price increases. Covers bank alerts, calendar reminders, and subscription tracking apps.",
            "category": "subscription_management",
            "rationale_template": "Subscriptions often increase prices after promotional periods. With {recurring_count} active subscriptions, alerts help you catch changes quickly.",
            "eligibility": {"min_recurring_count": 3},
        },
    ],
    "savings_builder": [
        {
            "title": "SMART Goal Setting for Financial Milestones",
            "description": "Apply the SMART framework (Specific, Measurable, Achievable, Relevant, Time-bound) to savings goals. Includes templates for emergency funds, down payments, and retirement.",
            "category": "goal_setting",
            "rationale_template": "You've grown your savings by {growth_rate_pct}% recently, showing strong momentum. SMART goals help channel that discipline toward specific milestones.",
            "eligibility": {"min_growth_rate_pct": 2},
        },
        {
            "title": "High-Yield Savings Accounts: Where to Find the Best Rates",
            "description": "Comparison of online banks offering 4-5% APY vs. traditional banks at 0.01%. Covers FDIC insurance, account minimums, and transfer times.",
            "category": "savings_optimization",
            "rationale_template": "With {net_inflow} saved in the last 6 months, moving to a high-yield account could earn you an extra $50-150/year in interest.",
            "eligibility": {"min_net_inflow": 500},
        },
        {
            "title": "Automating Your Savings: Set It and Forget It",
            "description": "How to automate transfers from checking to savings on payday. Includes tips for starting small and gradually increasing amounts.",
            "category": "savings_automation",
            "rationale_template": "Your savings inflow of {net_inflow} over 6 months shows you're already saving consistently. Automation makes it effortless.",
            "eligibility": {"min_net_inflow": 200},
        },
        {
            "title": "Certificates of Deposit (CDs): Locking In Higher Rates",
            "description": "When CDs make sense for part of your savings. Covers laddering strategies, penalty-free CDs, and how to balance liquidity with returns.",
            "category": "savings_optimization",
            "rationale_template": "With {emergency_fund_months} months of emergency savings, you may have excess funds that could earn higher rates in CDs.",
            "eligibility": {"min_emergency_fund_months": 4},
        },
        {
            "title": "The 50/30/20 Rule: Balancing Needs, Wants, and Savings",
            "description": "Popular budgeting framework: 50% needs, 30% wants, 20% savings/debt. Includes how to adapt percentages to your situation and track progress.",
            "category": "goal_setting",
            "rationale_template": "You're already saving {net_inflow} per month. The 50/30/20 rule can help you optimize other spending categories too.",
            "eligibility": {"min_net_inflow": 300},
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
            "rationale_template": "Phone service is often one of the biggest recurring bills. Mint Mobile could cut your phone costs by 50-70% without sacrificing coverage.",
            "eligibility": {
                "min_income_tier": "low",
                "min_recurring_count": 3,
            },
        },
    ],
    "savings_builder": [
        {
            "title": "Ally Bank High-Yield Savings Account",
            "description": "Top-rated online bank with competitive APY (4.0%+), no fees, no minimums, and excellent customer service. FDIC insured.",
            "category": "savings_account",
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
