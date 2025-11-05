"""
Configuration constants for SpendSense MVP V2.
Threshold values for behavioral signals, persona assignment, and evaluation.

All values derived from PRD Parts 2-3 specifications.
This is the single source of truth for tunable parameters.
"""

# =============================================================================
# PERSONA DETECTION THRESHOLDS (PRD Part 2, Section 6.1)
# =============================================================================

PERSONA_THRESHOLDS = {
    "High Utilization": {
        "utilization_threshold": 50.0,  # 50% or higher credit utilization
        "interest_threshold": 0.01,  # Any interest charges (> $0)
        "min_payment_only": True,  # Flag for minimum payment pattern
        "overdue_flag": True,  # Flag for overdue status
    },
    "Variable Income Budgeter": {
        "median_pay_gap_days": 45,  # More than 45 days between paychecks
        "cash_buffer_months": 1.0,  # Less than 1 month cash buffer
        "income_variability_threshold": 25.0,  # 25% std dev in income
    },
    "Subscription-Heavy": {
        "min_recurring_count": 3,  # At least 3 recurring merchants
        "recurring_spend_min": 50.0,  # At least $50/month OR
        "recurring_spend_pct": 10.0,  # 10% of total spend (percentage form to match feature output)
    },
    "Savings Builder": {
        "growth_rate_pct": 2.0,  # 2% or higher savings growth rate (percentage form to match feature output)
        "net_inflow_min": 200.0,  # At least $200 net inflow OR
        "max_utilization": 30.0,  # Credit utilization below 30% (percentage form: 30.0 = 30%)
    },
}

# Persona priority order for conflict resolution (PRD Part 2, Section 6.2)
PERSONA_PRIORITY = [
    "High Utilization",  # Priority 1: Immediate financial strain
    "Variable Income Budgeter",  # Priority 2: Stability and planning gap
    "Subscription-Heavy",  # Priority 3: Spending pattern optimization
    "Savings Builder",  # Priority 4: Positive reinforcement
    "General",  # Priority 5: Default for users with minimal signals
]

# =============================================================================
# TIME WINDOWS FOR ANALYSIS (PRD Part 2, Section 5)
# =============================================================================

TIME_WINDOWS = {
    "short_term_days": 30,  # 30-day rolling window for recent behavior
    "long_term_days": 180,  # 180-day (6 month) window for trends
}

# =============================================================================
# BEHAVIORAL SIGNAL DETECTION (PRD Part 2, Section 5)
# =============================================================================

# Subscription Detection
SUBSCRIPTION_DETECTION = {
    "min_occurrences": 3,  # Need 3+ occurrences to be considered recurring
    "lookback_days": 90,  # Look back 90 days for pattern detection
    "amount_variance_pct": 0.10,  # Allow 10% variance in amount for same merchant
}

# Savings Analysis
SAVINGS_ANALYSIS = {
    "emergency_fund_months": 3,  # Target emergency fund coverage
    "growth_calculation_days": 180,  # Calculate growth over 6 months
}

# Credit Utilization Flags (PRD Part 2, Section 5.3)
CREDIT_UTILIZATION_FLAGS = {
    "warning_threshold": 30.0,  # 30% utilization - yellow flag
    "high_threshold": 50.0,  # 50% utilization - orange flag
    "critical_threshold": 80.0,  # 80% utilization - red flag
}

# Income Stability Detection
INCOME_DETECTION = {
    "payroll_keywords": ["payroll", "direct dep", "salary", "wages"],
    "min_income_occurrences": 2,  # Need 2+ deposits to establish pattern
    "frequency_tolerance_days": 3,  # ±3 days for bi-weekly/monthly detection
}

# Subscription prices for common recurring merchants (used by generator)
SUBSCRIPTION_PRICES = {
    "Netflix": 15.99,
    "Spotify": 9.99,
    "Amazon Prime": 14.99,
    "Apple Music": 10.99,
    "Hulu": 7.99,
    "Disney+": 7.99,
    "NYT Subscription": 17.00,
    "WSJ": 29.99,
    "LA Fitness": 29.99,
    "Planet Fitness": 10.00,
    "Adobe Creative Cloud": 52.99,
    "Microsoft 365": 6.99,
    "Dropbox": 9.99,
    "LinkedIn Premium": 39.99,
}

# =============================================================================
# RECOMMENDATION ENGINE (PRD Part 2, Section 7)
# =============================================================================

RECOMMENDATION_LIMITS = {
    "education_items_min": 3,  # Minimum educational recommendations
    "education_items_max": 5,  # Maximum educational recommendations
    "partner_offers_min": 1,  # Minimum partner offers
    "partner_offers_max": 3,  # Maximum partner offers
}

# Content Types
RECOMMENDATION_TYPES = {
    "education": "education",
    "partner_offer": "partner_offer",
}

# =============================================================================
# GUARDRAILS & TONE VALIDATION (PRD Part 2, Section 8)
# =============================================================================

# Prohibited phrases (shaming language)
PROHIBITED_PHRASES = [
    "overspending",
    "bad habits",
    "lack discipline",
    "irresponsible",
    "wasteful",
    "poor choices",
    "financial mistakes",
    "careless",
]

# Preferred alternatives for tone correction
PREFERRED_ALTERNATIVES = {
    "overspending": "consider reducing spending",
    "bad habits": "habits to optimize",
    "lack discipline": "explore automation tools",
    "irresponsible": "opportunities to improve",
    "wasteful": "areas to optimize",
    "poor choices": "decisions to revisit",
    "financial mistakes": "learning opportunities",
    "careless": "attention to detail",
}

# Mandatory disclaimer for all recommendations (PRD Part 2, Section 8)
MANDATORY_DISCLAIMER = (
    "This is educational content, not financial advice. "
    "Consult a licensed advisor for personalized guidance."
)

# =============================================================================
# EVALUATION TARGETS (PRD Part 3, Section 10.1)
# =============================================================================

EVALUATION_TARGETS = {
    "coverage_pct": 100,  # 100% of users with persona + ≥3 behaviors
    "explainability_pct": 100,  # 100% of recommendations with rationale
    "relevance_pct": 90,  # 90% persona-content match score
    "latency_seconds": 5,  # < 5 seconds per user recommendation generation
    "fairness_variance_pct": 10,  # ±10% demographic parity
    "auditability_pct": 100,  # 100% of recommendations with trace JSON
}

# Fairness metrics demographic groups
FAIRNESS_DEMOGRAPHICS = [
    "age",
    "gender",
    "income_tier",
    "region",
]

# Minimum test count (PRD Part 2, Section 10)
MIN_TESTS_PASSING = 10  # Minimum 10 tests must pass

# =============================================================================
# ELIGIBILITY FILTERS (PRD Part 2, Section 8.2)
# =============================================================================

# Product eligibility rules
ELIGIBILITY_RULES = {
    "savings_account": {
        "min_income_tier": "low",  # Available to all income tiers
        "max_existing_savings": 2,  # Max 2 existing savings accounts
    },
    "credit_card": {
        "min_income_tier": "medium",  # Medium or high income only
        "max_credit_utilization": 0.80,  # No new cards if > 80% utilized
    },
    "budgeting_app": {
        "min_income_tier": "low",  # Available to all
    },
}

# Predatory products to exclude
PREDATORY_PRODUCTS = [
    "payday_loan",
    "title_loan",
    "rent_to_own",
    "high_fee_checking",  # > $15/month fees
]

# =============================================================================
# DATA GENERATION DEFAULTS (PRD Part 1, Section 4.1)
# =============================================================================

DEFAULT_GENERATION_CONFIG = {
    "seed": 42,  # Deterministic seed
    "num_users": 100,  # Default user count
    "months_history": 6,  # 6 months of transaction history
    "avg_transactions_per_month": 30,  # ~1 per day
}

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_CONFIG = {
    "default_page_size": 50,
    "max_page_size": 100,
    "timeout_seconds": 30,
}

# =============================================================================
# LOGGING & TRACING
# =============================================================================

TRACE_CONFIG = {
    "trace_dir": "docs/traces",
    "trace_format": "{user_id}.json",
    "include_timestamps": True,
    "include_raw_signals": True,
}
