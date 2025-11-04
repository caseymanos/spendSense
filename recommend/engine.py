"""
Recommendation Engine for SpendSense MVP V2

This module generates personalized educational content and partner offers
with explicit rationales citing user-specific behavioral data.

Core Functions:
- generate_recommendations(user_id): Main entry point
- _format_rationale(template, user_data): Inject concrete data into templates
- _apply_eligibility_filters(offers, user_data): Enforce eligibility rules
- _save_trace(user_id, recommendations): Update decision trace JSON

Design Principles:
- Every recommendation includes "because" rationale with actual user data
- Mandatory disclaimer appended to all recommendations
- Eligibility filters prevent inappropriate offers
- Full auditability via trace JSONs
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

from ingest.constants import (
    RECOMMENDATION_LIMITS,
    MANDATORY_DISCLAIMER,
    PREDATORY_PRODUCTS,
    TRACE_CONFIG,
)
from recommend.content_catalog import (
    get_education_items,
    get_partner_offers,
)


# Database path
DB_PATH = Path("data/users.sqlite")
SIGNALS_PATH = Path("features/signals.parquet")
TRANSACTIONS_PATH = Path("data/transactions.parquet")


def generate_recommendations(user_id: str) -> Dict[str, Any]:
    """
    Generate personalized recommendations for a user.

    Args:
        user_id: User identifier

    Returns:
        Dictionary containing:
        - user_id
        - persona
        - recommendations: List of education items and partner offers
        - metadata: generation timestamp, rationale count, etc.

    Returns empty recommendations list if:
    - User has 'general' persona (no strong signals)
    - User hasn't granted consent
    """
    # Load user context
    user_context = _load_user_context(user_id)

    # Check consent
    if not user_context.get("consent_granted", False):
        return {
            "user_id": user_id,
            "persona": user_context.get("persona", "unknown"),
            "recommendations": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "reason": "consent_not_granted",
            },
        }

    # Check persona
    persona = user_context.get("persona")
    if persona == "general" or persona is None:
        return {
            "user_id": user_id,
            "persona": persona or "unknown",
            "recommendations": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "reason": "general_persona_no_recommendations",
            },
        }

    # Select education items (3-5)
    education_recs = _select_education_items(persona, user_context)

    # Select partner offers (1-3) with eligibility filtering
    offer_recs = _select_partner_offers(persona, user_context)

    # Combine recommendations
    all_recommendations = education_recs + offer_recs

    # Append disclaimer to all
    all_recommendations = _append_disclaimer(all_recommendations)

    # Build response
    response = {
        "user_id": user_id,
        "persona": persona,
        "recommendations": all_recommendations,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "education_count": len(education_recs),
            "offer_count": len(offer_recs),
            "total_count": len(all_recommendations),
        },
    }

    # If we couldn't meet minimum education items due to insufficient data/signals,
    # add explicit metadata reason rather than padding with ineligible items.
    min_items = RECOMMENDATION_LIMITS["education_items_min"]
    if len(education_recs) < min_items:
        shortfall = max(0, min_items - len(education_recs))
        response["metadata"]["reason"] = "insufficient_data"
        response["metadata"]["education_eligibility_shortfall"] = shortfall
        response["metadata"]["signals_present"] = SIGNALS_PATH.exists()

    # Save trace
    _save_trace(user_id, response, user_context)

    return response


def _load_user_context(user_id: str) -> Dict[str, Any]:
    """
    Load all relevant data for a user from SQLite, Parquet, and transactions.

    Returns:
        Dictionary with:
        - user_id
        - persona
        - consent_granted
        - income_tier
        - signals: behavioral metrics from features/signals.parquet
        - accounts: list of account dicts
        - transactions: recent transactions for merchant details
    """
    context = {"user_id": user_id}

    # Load from SQLite
    with sqlite3.connect(DB_PATH) as conn:
        # Get user demographics and consent
        user_row = pd.read_sql(
            "SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,)
        )
        if len(user_row) > 0:
            context["consent_granted"] = bool(user_row.iloc[0]["consent_granted"])
            context["income_tier"] = user_row.iloc[0].get("income_tier", "low")
            context["age"] = user_row.iloc[0].get("age")
            context["gender"] = user_row.iloc[0].get("gender")
            context["region"] = user_row.iloc[0].get("region")
        else:
            context["consent_granted"] = False
            context["income_tier"] = "low"

        # Get persona assignment
        persona_row = pd.read_sql(
            "SELECT * FROM persona_assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT 1",
            conn,
            params=(user_id,),
        )
        if len(persona_row) > 0:
            context["persona"] = persona_row.iloc[0]["persona"]
            context["criteria_met"] = json.loads(
                persona_row.iloc[0].get("criteria_met", "[]")
            )
        else:
            context["persona"] = None
            context["criteria_met"] = []

        # Get accounts
        accounts_df = pd.read_sql(
            "SELECT * FROM accounts WHERE user_id = ?", conn, params=(user_id,)
        )
        context["accounts"] = accounts_df.to_dict("records") if len(accounts_df) > 0 else []

        # Count existing account types for eligibility
        context["existing_account_types"] = {}
        if len(accounts_df) > 0:
            account_type_counts = accounts_df["account_type"].value_counts().to_dict()
            context["existing_account_types"] = account_type_counts

    # Load signals from Parquet
    if SIGNALS_PATH.exists():
        signals_df = pd.read_parquet(SIGNALS_PATH)
        user_signals = signals_df[signals_df["user_id"] == user_id]
        if len(user_signals) > 0:
            # Convert to dict, excluding user_id
            signals_dict = user_signals.iloc[0].to_dict()
            signals_dict.pop("user_id", None)
            context["signals"] = signals_dict
        else:
            context["signals"] = {}
    else:
        context["signals"] = {}

    # Load recent transactions for merchant details (last 30 days for rationales)
    if TRANSACTIONS_PATH.exists() and len(accounts_df) > 0:
        transactions_df = pd.read_parquet(TRANSACTIONS_PATH)
        # Get user's account IDs
        user_account_ids = accounts_df["account_id"].tolist()
        # Filter transactions for user's accounts
        user_txns = transactions_df[transactions_df["account_id"].isin(user_account_ids)]
        if len(user_txns) > 0:
            # Sort by date descending, take last 30 days
            user_txns = user_txns.sort_values("date", ascending=False)
            user_txns["date"] = pd.to_datetime(user_txns["date"])
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30)
            recent_txns = user_txns[user_txns["date"] >= cutoff_date]
            context["recent_transactions"] = recent_txns.to_dict("records")
        else:
            context["recent_transactions"] = []
    else:
        context["recent_transactions"] = []

    return context


def _select_education_items(
    persona: str, user_context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Select 3-5 educational items for the persona, filtering by eligibility.

    Args:
        persona: User's assigned persona
        user_context: Full user context with signals and accounts

    Returns:
        List of recommendation dicts with type, title, rationale, disclaimer
    """
    all_items = get_education_items(persona)
    signals = user_context.get("signals", {})

    # Filter by eligibility
    eligible_items = []
    for item in all_items:
        if _check_content_eligibility(item, signals, user_context):
            eligible_items.append(item)

    # Limit to 3-5 items
    min_items = RECOMMENDATION_LIMITS["education_items_min"]
    max_items = RECOMMENDATION_LIMITS["education_items_max"]

    # Take top items (already prioritized in catalog order)
    selected_items = eligible_items[:max_items]

    # Format recommendations with rationales
    recommendations = []
    for item in selected_items:
        rationale = _format_rationale(
            item["rationale_template"], user_context, item.get("category")
        )
        recommendations.append(
            {
                "type": "education",
                "title": item["title"],
                "description": item["description"],
                "category": item.get("category", "general"),
                "rationale": rationale,
            }
        )

    return recommendations


def _select_partner_offers(
    persona: str, user_context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Select 1-3 partner offers for the persona, applying strict eligibility filters.

    Args:
        persona: User's assigned persona
        user_context: Full user context with signals and accounts

    Returns:
        List of offer recommendation dicts
    """
    all_offers = get_partner_offers(persona)
    signals = user_context.get("signals", {})
    income_tier = user_context.get("income_tier", "low")

    # Filter by eligibility
    eligible_offers = []
    for offer in all_offers:
        if _check_offer_eligibility(offer, signals, user_context, income_tier):
            eligible_offers.append(offer)

    # Limit to 1-3 offers
    min_offers = RECOMMENDATION_LIMITS["partner_offers_min"]
    max_offers = RECOMMENDATION_LIMITS["partner_offers_max"]

    selected_offers = eligible_offers[:max_offers]

    # Format recommendations with rationales
    recommendations = []
    for offer in selected_offers:
        rationale = _format_rationale(
            offer["rationale_template"], user_context, offer.get("category")
        )
        recommendations.append(
            {
                "type": "partner_offer",
                "title": offer["title"],
                "description": offer["description"],
                "category": offer.get("category", "general"),
                "rationale": rationale,
            }
        )

    return recommendations


def _check_content_eligibility(
    item: Dict[str, Any], signals: Dict[str, Any], user_context: Dict[str, Any]
) -> bool:
    """
    Check if educational content is relevant based on eligibility criteria.

    Args:
        item: Content item with eligibility dict
        signals: User behavioral signals
        user_context: Full user context

    Returns:
        True if eligible, False otherwise
    """
    eligibility = item.get("eligibility", {})

    # Check minimum thresholds
    if "min_utilization" in eligibility:
        max_util = signals.get("credit_max_util_pct", 0) / 100.0
        if max_util < eligibility["min_utilization"]:
            return False

    if "min_cards" in eligibility:
        num_cards = signals.get("credit_num_cards", 0)
        if num_cards < eligibility["min_cards"]:
            return False

    if "has_interest_charges" in eligibility:
        # Check if user has interest charges
        # This would be in liabilities table, approximate with high utilization
        max_util = signals.get("credit_max_util_pct", 0) / 100.0
        if eligibility["has_interest_charges"] and max_util < 0.30:
            return False

    if "min_pay_gap_days" in eligibility:
        pay_gap = signals.get("inc_180d_median_pay_gap_days", 0)
        if pay_gap < eligibility["min_pay_gap_days"]:
            return False

    if "max_cash_buffer_months" in eligibility:
        buffer = signals.get("inc_180d_cash_buffer_months", 999)
        if buffer > eligibility["max_cash_buffer_months"]:
            return False

    if "min_recurring_count" in eligibility:
        recurring = signals.get("sub_180d_recurring_count", 0)
        if recurring < eligibility["min_recurring_count"]:
            return False

    if "min_subscription_share_pct" in eligibility:
        share = signals.get("sub_180d_share_pct", 0)
        if share < eligibility["min_subscription_share_pct"]:
            return False

    if "min_monthly_recurring_spend" in eligibility:
        spend = signals.get("sub_180d_monthly_spend", 0)
        if spend < eligibility["min_monthly_recurring_spend"]:
            return False

    if "min_growth_rate_pct" in eligibility:
        growth = signals.get("sav_180d_growth_rate_pct", 0)
        if growth < eligibility["min_growth_rate_pct"]:
            return False

    if "min_net_inflow" in eligibility:
        inflow = signals.get("sav_180d_net_inflow", 0)
        if inflow < eligibility["min_net_inflow"]:
            return False

    if "min_emergency_fund_months" in eligibility:
        ef_months = signals.get("sav_180d_emergency_fund_months", 0)
        if ef_months < eligibility["min_emergency_fund_months"]:
            return False

    return True


def _check_offer_eligibility(
    offer: Dict[str, Any],
    signals: Dict[str, Any],
    user_context: Dict[str, Any],
    income_tier: str,
) -> bool:
    """
    Apply strict eligibility filters to partner offers.

    Args:
        offer: Offer dict with eligibility rules
        signals: User behavioral signals
        user_context: Full user context
        income_tier: User's income tier (low, medium, high)

    Returns:
        True if eligible, False otherwise
    """
    eligibility = offer.get("eligibility", {})

    # Check income tier requirement
    if "min_income_tier" in eligibility:
        tier_order = {"low": 0, "medium": 1, "high": 2}
        user_tier_level = tier_order.get(income_tier, 0)
        required_tier_level = tier_order.get(eligibility["min_income_tier"], 0)
        if user_tier_level < required_tier_level:
            return False

    # Check if user already has this type of account
    if "exclude_existing" in eligibility:
        existing_types = user_context.get("existing_account_types", {})
        for excluded_type in eligibility["exclude_existing"]:
            # Check account types or categories
            if excluded_type in existing_types:
                return False

    # Check max existing savings accounts
    if "max_existing_savings_accounts" in eligibility:
        existing_savings = user_context.get("existing_account_types", {}).get(
            "savings", 0
        )
        if existing_savings >= eligibility["max_existing_savings_accounts"]:
            return False

    # Check utilization thresholds
    if "min_utilization" in eligibility:
        avg_util = signals.get("credit_avg_util_pct", 0) / 100.0
        if avg_util < eligibility["min_utilization"]:
            return False

    if "max_utilization" in eligibility:
        max_util = signals.get("credit_max_util_pct", 0) / 100.0
        if max_util > eligibility["max_utilization"]:
            return False

    if "max_credit_utilization" in eligibility:
        avg_util = signals.get("credit_avg_util_pct", 0) / 100.0
        if avg_util > eligibility["max_credit_utilization"]:
            return False

    # Check subscription-related thresholds
    if "min_recurring_count" in eligibility:
        recurring = signals.get("sub_180d_recurring_count", 0)
        if recurring < eligibility["min_recurring_count"]:
            return False

    if "min_subscription_share_pct" in eligibility:
        share = signals.get("sub_180d_share_pct", 0)
        if share < eligibility["min_subscription_share_pct"]:
            return False

    # Check income-related thresholds
    if "min_pay_gap_days" in eligibility:
        pay_gap = signals.get("inc_180d_median_pay_gap_days", 0)
        if pay_gap < eligibility["min_pay_gap_days"]:
            return False

    # Check savings-related thresholds
    if "min_net_inflow" in eligibility:
        inflow = signals.get("sav_180d_net_inflow", 0)
        if inflow < eligibility["min_net_inflow"]:
            return False

    if "min_emergency_fund_months" in eligibility:
        ef_months = signals.get("sav_180d_emergency_fund_months", 0)
        if ef_months < eligibility["min_emergency_fund_months"]:
            return False

    if "min_growth_rate_pct" in eligibility:
        growth = signals.get("sav_180d_growth_rate_pct", 0)
        if growth < eligibility["min_growth_rate_pct"]:
            return False

    # Check number of cards
    if "min_cards" in eligibility:
        num_cards = signals.get("credit_num_cards", 0)
        if num_cards < eligibility["min_cards"]:
            return False

    # Exclude predatory products (shouldn't be in catalog, but double-check)
    category = offer.get("category", "")
    if category in PREDATORY_PRODUCTS:
        return False

    return True


def _format_rationale(
    template: str, user_context: Dict[str, Any], category: Optional[str] = None
) -> str:
    """
    Inject concrete user data into rationale template.

    Args:
        template: Rationale template with {placeholder} variables
        user_context: Full user context with signals, accounts, transactions
        category: Content category (e.g., 'credit_basics', 'subscriptions')

    Returns:
        Formatted rationale string with actual user data
    """
    signals = user_context.get("signals", {})
    accounts = user_context.get("accounts", [])
    recent_txns = user_context.get("recent_transactions", [])

    # Build replacement dict
    replacements = {}

    # Credit-related data
    if "{utilization_pct}" in template or "{card_description}" in template:
        # Find card with highest utilization
        credit_cards = [a for a in accounts if a.get("account_type") == "credit"]
        if credit_cards:
            # Calculate utilization per card
            for card in credit_cards:
                balance = card.get("balance_current", 0)
                limit = card.get("balance_limit", 1)
                card["utilization"] = (balance / limit * 100) if limit > 0 else 0

            # Get card with max utilization
            max_util_card = max(credit_cards, key=lambda c: c.get("utilization", 0))
            replacements["{card_description}"] = f"{max_util_card.get('account_subtype', 'card')} ending in {max_util_card.get('mask', 'XXXX')}"
            replacements["{utilization_pct}"] = f"{max_util_card.get('utilization', 0):.0f}"
            replacements["{balance}"] = f"${max_util_card.get('balance_current', 0):,.0f}"
            replacements["{limit}"] = f"${max_util_card.get('balance_limit', 0):,.0f}"

    replacements["{avg_utilization_pct}"] = f"{signals.get('credit_avg_util_pct', 0):.0f}"
    replacements["{num_cards}"] = str(int(signals.get("credit_num_cards", 0)))

    # Estimate monthly interest (approximate)
    avg_util_pct = signals.get("credit_avg_util_pct", 0)
    credit_cards = [a for a in accounts if a.get("account_type") == "credit"]
    if credit_cards:
        total_balance = sum(c.get("balance_current", 0) for c in credit_cards)
        # Assume 18% APR average
        monthly_interest = total_balance * (0.18 / 12)
        replacements["{monthly_interest}"] = f"${monthly_interest:.0f}/month"
        # Estimate savings from balance transfer
        replacements["{estimated_savings}"] = f"${monthly_interest * 12:.0f}"
    else:
        replacements["{monthly_interest}"] = "$0/month"
        replacements["{estimated_savings}"] = "$0"

    # Income-related data
    replacements["{pay_gap_days}"] = str(int(signals.get("inc_180d_median_pay_gap_days", 0)))
    replacements["{cash_buffer_months}"] = f"{signals.get('inc_180d_cash_buffer_months', 0):.1f}"
    replacements["{avg_paycheck}"] = f"${signals.get('inc_180d_avg_paycheck', 0):,.0f}"

    # Subscription-related data
    replacements["{recurring_count}"] = str(int(signals.get("sub_180d_recurring_count", 0)))
    replacements["{monthly_recurring_spend}"] = f"${signals.get('sub_180d_monthly_spend', 0):,.0f}"
    replacements["{subscription_share_pct}"] = f"{signals.get('sub_180d_share_pct', 0):.0f}"

    # Savings-related data
    replacements["{net_inflow}"] = f"${signals.get('sav_180d_net_inflow', 0):,.0f}"
    replacements["{growth_rate_pct}"] = f"{signals.get('sav_180d_growth_rate_pct', 0):.1f}"
    replacements["{emergency_fund_months}"] = f"{signals.get('sav_180d_emergency_fund_months', 0):.1f}"

    # Apply replacements
    formatted = template
    for placeholder, value in replacements.items():
        formatted = formatted.replace(placeholder, value)

    return formatted


def _append_disclaimer(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Append mandatory disclaimer to all recommendations.

    Args:
        recommendations: List of recommendation dicts

    Returns:
        Same list with 'disclaimer' field added to each
    """
    for rec in recommendations:
        rec["disclaimer"] = MANDATORY_DISCLAIMER

    return recommendations


def _save_trace(
    user_id: str, response: Dict[str, Any], user_context: Dict[str, Any]
) -> None:
    """
    Update user's trace JSON with recommendation details.

    Args:
        user_id: User identifier
        response: Full recommendation response
        user_context: User context used for generation
    """
    trace_dir = Path(TRACE_CONFIG["trace_dir"])
    trace_dir.mkdir(parents=True, exist_ok=True)

    trace_file = trace_dir / f"{user_id}.json"

    # Load existing trace or create new
    if trace_file.exists():
        with open(trace_file, "r") as f:
            trace_data = json.load(f)
    else:
        trace_data = {"user_id": user_id}

    # Add recommendation section (matching PR #2 and PR #3 pattern)
    trace_data["recommendations"] = {
        "timestamp": datetime.now().isoformat(),
        "persona": response.get("persona"),
        "education_count": response["metadata"]["education_count"],
        "offer_count": response["metadata"]["offer_count"],
        "total_recommendations": response["metadata"]["total_count"],
        "recommendations": response["recommendations"],
        "consent_granted": user_context.get("consent_granted", False),
    }

    # Save trace
    with open(trace_file, "w") as f:
        json.dump(trace_data, f, indent=2)


# ============================================
# BATCH PROCESSING
# ============================================


def generate_all_recommendations(output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Generate recommendations for all users in the system.

    Args:
        output_path: Optional path to save recommendations JSON

    Returns:
        DataFrame with recommendations for all users
    """
    # Load all user IDs
    with sqlite3.connect(DB_PATH) as conn:
        users_df = pd.read_sql("SELECT user_id FROM users", conn)

    all_recommendations = []

    for user_id in users_df["user_id"]:
        rec_response = generate_recommendations(user_id)
        all_recommendations.append(rec_response)

    # Convert to DataFrame
    recs_df = pd.DataFrame(all_recommendations)

    # Save if requested
    if output_path:
        output_path = Path(output_path)
        if output_path.suffix == ".json":
            recs_df.to_json(output_path, orient="records", indent=2)
        elif output_path.suffix == ".parquet":
            recs_df.to_parquet(output_path, index=False)

    return recs_df
