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
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

from ingest.constants import (
    RECOMMENDATION_LIMITS,
    MANDATORY_DISCLAIMER,
    PREDATORY_PRODUCTS,
    TRACE_CONFIG,
)
from recommend.chart_generator import ChartGenerator
from recommend.content_loader import (
    get_education_items,
    get_partner_offers,
)
from guardrails.tone import scan_recommendations
from guardrails.eligibility import filter_predatory_products


# Database path - use absolute paths from project root
_PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = _PROJECT_ROOT / "data" / "users.sqlite"
SIGNALS_PATH = _PROJECT_ROOT / "features" / "signals.parquet"
TRANSACTIONS_PATH = _PROJECT_ROOT / "data" / "transactions.parquet"

# Logger
logger = logging.getLogger(__name__)

# Chart Generator (Plotly-based visualization)
CHART_GENERATOR = ChartGenerator(output_dir=str(_PROJECT_ROOT / "data" / "images"))
logger.info("Chart generator initialized (Plotly)")

NO_CONSENT_MESSAGE = (
    "Consent not granted. Opt in from your profile to unlock personalized guidance."
)
NO_RECOMMENDATIONS_MESSAGE = "You're doing great - no recommendations at this time."


def _build_empty_response(
    user_id: str,
    persona: Optional[str],
    reason: str,
    message: str,
    consent_granted: bool,
) -> Dict[str, Any]:
    """
    Construct a standardized empty recommendation payload so traces remain complete.
    """
    timestamp = datetime.now().isoformat()
    return {
        "user_id": user_id,
        "persona": persona or "unknown",
        "recommendations": [],
        "metadata": {
            "timestamp": timestamp,
            "reason": reason,
            "message": message,
            "education_count": 0,
            "offer_count": 0,
            "total_count": 0,
            "tone_check_passed": None,
            "tone_violations_count": 0,
            "consent_granted": consent_granted,
        },
    }


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

    consent_granted = bool(user_context.get("consent_granted", False))
    persona = user_context.get("persona")
    if not consent_granted:
        response = _build_empty_response(
            user_id,
            persona,
            reason="consent_not_granted",
            message=NO_CONSENT_MESSAGE,
            consent_granted=False,
        )
        _save_trace(user_id, response, user_context)
        return response

    # Check persona
    if persona == "general" or persona is None:
        response = _build_empty_response(
            user_id,
            persona,
            reason="general_persona_no_recommendations",
            message=NO_RECOMMENDATIONS_MESSAGE,
            consent_granted=True,
        )
        _save_trace(user_id, response, user_context)
        return response

    # Select education items (3-5)
    education_recs = _select_education_items(persona, user_context)

    # Select partner offers (1-3) with eligibility filtering
    offer_recs = _select_partner_offers(persona, user_context)

    # Deduplicate and enforce diversity
    education_recs, offer_recs = _deduplicate_and_enforce_diversity(education_recs, offer_recs)

    # Combine recommendations
    all_recommendations = education_recs + offer_recs

    # GUARDRAIL: Tone validation (scan for prohibited phrases)
    tone_scan = scan_recommendations(all_recommendations)
    if not tone_scan["passed"]:
        # Log tone violations for operator review
        _log_tone_violations(user_id, tone_scan)

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
            "tone_check_passed": tone_scan["passed"],
            "tone_violations_count": tone_scan.get("violations_found", 0),
            "consent_granted": consent_granted,
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

    if response["metadata"]["total_count"] == 0:
        response["metadata"].setdefault("reason", "no_recommendations_available")
        response["metadata"].setdefault("message", NO_RECOMMENDATIONS_MESSAGE)

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
        user_row = pd.read_sql("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))
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
            context["criteria_met"] = json.loads(persona_row.iloc[0].get("criteria_met", "[]"))
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


def _select_education_items(persona: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
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

    # Score each eligible item for relevance
    scored_items = []
    for item in eligible_items:
        score = _score_recommendation(item, signals, user_context, "education")
        scored_items.append((item, score))

    # Sort by score descending (highest relevance first)
    scored_items.sort(key=lambda x: x[1], reverse=True)

    # Limit to 3-5 items
    min_items = RECOMMENDATION_LIMITS["education_items_min"]
    max_items = RECOMMENDATION_LIMITS["education_items_max"]

    # Take top items by score
    selected_items = [item for item, score in scored_items[:max_items]]

    # Format recommendations with rationales
    recommendations = []
    for item in selected_items:
        rationale = _format_rationale(
            item["rationale_template"], user_context, item.get("category")
        )
        rec = {
            "type": "education",
            "title": item["title"],
            "description": item["description"],
            "category": item.get("category", "general"),
            "topic": item.get("topic", "general"),
            "partner_equivalent": item.get("partner_equivalent", False),
            "rationale": rationale,
        }

        # Generate chart for supported topics
        topic = item.get("topic", "general")
        if topic in ["credit_utilization", "debt_paydown_strategy", "emergency_fund", "subscription_audit", "automation"]:
            try:
                chart_result = _generate_chart_for_topic(topic, persona, user_context)
                if chart_result.get("success"):
                    rec["chart_path"] = chart_result["chart_path"]
                    rec["chart_html"] = chart_result["html_path"]
                    logger.info(f"Chart generated for {topic}: {chart_result['chart_path']}")
                else:
                    logger.warning(f"Chart generation failed for {topic}: {chart_result.get('error')}")
            except Exception as e:
                logger.warning(f"Chart generation exception for {topic}: {e}")

        recommendations.append(rec)

    return recommendations


def _select_partner_offers(persona: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
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

    # GUARDRAIL: Filter out predatory products
    safe_offers, blocked_offers = filter_predatory_products(all_offers)

    # Log blocked predatory products if any
    if blocked_offers:
        user_id = user_context.get("user_id", "unknown")
        _log_blocked_offers(user_id, blocked_offers, "predatory_product")

    # Filter by eligibility
    eligible_offers = []
    for offer in safe_offers:
        if _check_offer_eligibility(offer, signals, user_context, income_tier):
            eligible_offers.append(offer)

    # Score each eligible offer for relevance
    scored_offers = []
    for offer in eligible_offers:
        score = _score_recommendation(offer, signals, user_context, "partner_offer")
        scored_offers.append((offer, score))

    # Sort by score descending (highest relevance first)
    scored_offers.sort(key=lambda x: x[1], reverse=True)

    # Limit to 1-3 offers
    min_offers = RECOMMENDATION_LIMITS["partner_offers_min"]
    max_offers = RECOMMENDATION_LIMITS["partner_offers_max"]

    # Take top offers by score
    selected_offers = [offer for offer, score in scored_offers[:max_offers]]

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
                "topic": offer.get("topic", "general"),
                "rationale": rationale,
            }
        )

    return recommendations


def _score_recommendation(
    item: Dict[str, Any],
    signals: Dict[str, Any],
    user_context: Dict[str, Any],
    rec_type: str,
) -> float:
    """
    Calculate relevance score for a recommendation based on user signals.

    Higher scores indicate more relevant/urgent recommendations.

    Args:
        item: Recommendation item (education or partner offer)
        signals: User behavioral signals
        user_context: Full user context
        rec_type: "education" or "partner_offer"

    Returns:
        Relevance score (0-100, higher is more relevant)
    """
    score = 50.0  # Base score
    category = item.get("category", "general")
    topic = item.get("topic", "general")

    # CREDIT-RELATED SCORING
    if category in ["credit_basics", "debt_paydown", "credit_card"]:
        util_pct = signals.get("credit_avg_util_pct", 0)
        # High utilization = higher urgency
        if util_pct > 70:
            score += 30  # Critical urgency
        elif util_pct > 50:
            score += 20  # High urgency
        elif util_pct > 30:
            score += 10  # Moderate urgency

        # Estimate potential monthly interest savings
        num_cards = signals.get("credit_num_cards", 0)
        if num_cards > 0:
            accounts = user_context.get("accounts", [])
            credit_cards = [a for a in accounts if a.get("account_type") == "credit"]
            if credit_cards:
                total_balance = sum(c.get("balance_current", 0) for c in credit_cards)
                monthly_interest = total_balance * (0.18 / 12)
                # Add up to 15 points based on potential savings
                score += min(15, monthly_interest / 20)

    # SUBSCRIPTION-RELATED SCORING
    elif category in ["subscription_management", "subscription_app"]:
        recurring_count = signals.get("sub_180d_recurring_count", 0)
        monthly_spend = signals.get("sub_180d_monthly_spend", 0)
        share_pct = signals.get("sub_180d_share_pct", 0)

        # More subscriptions = higher relevance
        if recurring_count >= 6:
            score += 20
        elif recurring_count >= 4:
            score += 10

        # Higher spend = more potential savings
        if monthly_spend > 200:
            score += 15
        elif monthly_spend > 100:
            score += 10

        # High subscription share indicates opportunity
        if share_pct > 15:
            score += 10

    # SAVINGS-RELATED SCORING
    elif category in ["savings_optimization", "savings_account", "cd_account", "investment_account"]:
        net_inflow = signals.get("sav_180d_net_inflow", 0)
        growth_rate = signals.get("sav_180d_growth_rate_pct", 0)
        emergency_fund = signals.get("sav_180d_emergency_fund_months", 0)

        # Positive savings behavior = higher relevance
        if net_inflow > 2000:
            score += 20  # Significant savings
        elif net_inflow > 1000:
            score += 15
        elif net_inflow > 500:
            score += 10

        # Growth rate indicates engagement
        if growth_rate > 5:
            score += 10
        elif growth_rate > 3:
            score += 5

        # Strong emergency fund = ready for optimization
        if emergency_fund >= 6 and topic == "cd_accounts":
            score += 15  # Ready to lock in some funds
        elif emergency_fund >= 5 and topic == "investment_account":
            score += 10  # Ready to invest beyond emergency fund

    # INCOME-RELATED SCORING
    elif category in ["budgeting", "tax_planning", "tax_app", "emergency_fund"]:
        pay_gap = signals.get("inc_180d_median_pay_gap_days", 0)
        cash_buffer = signals.get("inc_180d_cash_buffer_months", 0)

        # Longer pay gaps = higher urgency
        if pay_gap > 45:
            score += 25
        elif pay_gap > 35:
            score += 15
        elif pay_gap > 30:
            score += 10

        # Low cash buffer = higher urgency for emergency fund content
        if topic in ["emergency_fund_variable_income", "emergency_fund_calculator"]:
            if cash_buffer < 2:
                score += 20
            elif cash_buffer < 4:
                score += 10

    # PARTNER OFFER PREMIUM
    # Partner offers get slight boost if they solve an immediate need
    if rec_type == "partner_offer":
        score += 5

    return score


def _deduplicate_and_enforce_diversity(
    education_recs: List[Dict[str, Any]],
    offer_recs: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove duplicate topics and enforce diversity across recommendations.

    Rules:
    1. If an education item has partner_equivalent=True AND a partner offer exists
       with the same topic, remove the education item (keep the actionable offer)
    2. Max 2 items per category across education + offers combined

    Args:
        education_recs: List of education recommendations
        offer_recs: List of partner offer recommendations

    Returns:
        Tuple of (deduplicated_education, deduplicated_offers)
    """
    # Build topic sets
    offer_topics = {rec.get("topic") for rec in offer_recs if rec.get("topic")}

    # Remove education items that have partner equivalents
    filtered_education = []
    for rec in education_recs:
        topic = rec.get("topic")
        has_partner = rec.get("partner_equivalent", False)

        # If this education item has a partner offer with same topic, skip it
        if has_partner and topic in offer_topics:
            continue  # Skip - offer is more actionable
        else:
            filtered_education.append(rec)

    # Enforce category diversity (max 2 per category)
    category_counts = {}
    final_education = []
    final_offers = []

    # Process offers first (higher priority)
    for rec in offer_recs:
        category = rec.get("category", "general")
        count = category_counts.get(category, 0)
        if count < 2:
            final_offers.append(rec)
            category_counts[category] = count + 1

    # Process education items
    for rec in filtered_education:
        category = rec.get("category", "general")
        count = category_counts.get(category, 0)
        if count < 2:
            final_education.append(rec)
            category_counts[category] = count + 1

    return final_education, final_offers


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
        existing_savings = user_context.get("existing_account_types", {}).get("savings", 0)
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
            replacements["{card_description}"] = (
                f"{max_util_card.get('account_subtype', 'card')} ending in {max_util_card.get('mask', 'XXXX')}"
            )
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
    replacements["{emergency_fund_months}"] = (
        f"{signals.get('sav_180d_emergency_fund_months', 0):.1f}"
    )

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


def _save_trace(user_id: str, response: Dict[str, Any], user_context: Dict[str, Any]) -> None:
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
        "timestamp": response["metadata"].get("timestamp", datetime.now().isoformat()),
        "persona": response.get("persona"),
        "education_count": response["metadata"]["education_count"],
        "offer_count": response["metadata"]["offer_count"],
        "total_recommendations": response["metadata"]["total_count"],
        "recommendations": response["recommendations"],
        "consent_granted": user_context.get("consent_granted", False),
        "source": response["metadata"].get("source", "rule_based"),  # Track source (AI vs rule-based)
    }
    if "reason" in response["metadata"]:
        trace_data["recommendations"]["reason"] = response["metadata"]["reason"]
    if "message" in response["metadata"]:
        trace_data["recommendations"]["message"] = response["metadata"]["message"]
    if "education_eligibility_shortfall" in response["metadata"]:
        trace_data["recommendations"]["education_shortfall"] = response["metadata"][
            "education_eligibility_shortfall"
        ]
    # Include AI-specific metadata if available
    if "token_usage" in response["metadata"]:
        trace_data["recommendations"]["token_usage"] = response["metadata"]["token_usage"]
    if "model" in response["metadata"]:
        trace_data["recommendations"]["model"] = response["metadata"]["model"]

    # Save trace
    with open(trace_file, "w") as f:
        json.dump(trace_data, f, indent=2)


def _log_blocked_offers(
    user_id: str, blocked_offers: List[Dict[str, Any]], reason_type: str
) -> None:
    """
    Log blocked partner offers to user's trace file.

    Args:
        user_id: User identifier
        blocked_offers: List of blocked offer dicts from guardrails
        reason_type: Type of block (e.g., "predatory_product", "eligibility")
    """
    trace_file = Path(TRACE_CONFIG["trace_dir"]) / f"{user_id}.json"

    # Load existing trace if it exists
    if trace_file.exists():
        with open(trace_file, "r") as f:
            trace_data = json.load(f)
    else:
        trace_data = {"user_id": user_id}

    # Ensure guardrail_decisions list exists
    if "guardrail_decisions" not in trace_data:
        trace_data["guardrail_decisions"] = []

    # Add blocked offers entry
    trace_data["guardrail_decisions"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "decision_type": "offers_blocked",
            "reason_type": reason_type,
            "blocked_count": len(blocked_offers),
            "blocked_offers": [
                {
                    "title": b["offer"].get("title", "Unknown"),
                    "product_type": b["offer"].get("product_type", "Unknown"),
                    "reason": b["reason"],
                    "blocked_at": b.get("blocked_at", reason_type),
                }
                for b in blocked_offers
            ],
        }
    )

    # Save trace
    with open(trace_file, "w") as f:
        json.dump(trace_data, f, indent=2)


def _log_tone_violations(user_id: str, tone_scan: Dict[str, Any]) -> None:
    """
    Log tone violations to user's trace file for operator review.

    Args:
        user_id: User identifier
        tone_scan: Tone scan result dict from guardrails
    """
    trace_file = Path(TRACE_CONFIG["trace_dir"]) / f"{user_id}.json"

    # Load existing trace if it exists
    if trace_file.exists():
        with open(trace_file, "r") as f:
            trace_data = json.load(f)
    else:
        trace_data = {"user_id": user_id}

    # Ensure guardrail_decisions list exists
    if "guardrail_decisions" not in trace_data:
        trace_data["guardrail_decisions"] = []

    # Add tone violations entry
    trace_data["guardrail_decisions"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "decision_type": "tone_violations",
            "violations_found": tone_scan.get("violations_found", 0),
            "details": tone_scan.get("details", []),
        }
    )

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


def _generate_chart_for_topic(topic: str, persona: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Plotly chart for a specific topic.

    Args:
        topic: Topic identifier (credit_utilization, debt_paydown_strategy, etc.)
        persona: User's persona
        user_context: User context with signals and account data

    Returns:
        Dict with success, chart_path, html_path, or error
    """
    signals = user_context.get("signals", {})

    try:
        if topic == "credit_utilization":
            # Extract card data
            card_mask = "XXXX"
            liabilities = user_context.get("liabilities", [])
            if liabilities:
                highest_util_card = max(liabilities, key=lambda x: x.get("utilization_pct", 0))
                account_number = highest_util_card.get("account_number", "")
                if len(account_number) >= 4:
                    card_mask = account_number[-4:]

            utilization_pct = signals.get("credit_max_util_pct", 50)
            return CHART_GENERATOR.generate_credit_utilization_gauge(
                utilization_pct=utilization_pct,
                card_mask=card_mask
            )

        elif topic == "debt_paydown_strategy":
            # Use balance data from context
            balance_high = "$7,500"  # Default
            balance_low = "$2,100"   # Default

            liabilities = user_context.get("liabilities", [])
            if len(liabilities) >= 2:
                # Sort by balance descending
                sorted_liabs = sorted(liabilities, key=lambda x: x.get("balance", 0), reverse=True)
                balance_high = f"${sorted_liabs[0].get('balance', 7500):,.0f}"
                balance_low = f"${sorted_liabs[1].get('balance', 2100):,.0f}"

            return CHART_GENERATOR.generate_debt_avalanche_comparison(
                balance_high=balance_high,
                balance_low=balance_low
            )

        elif topic == "emergency_fund":
            # Calculate current emergency fund months
            current_months = 0  # Could calculate from savings balance / monthly expenses
            return CHART_GENERATOR.generate_emergency_fund_progress(
                current_months=current_months,
                target_months=6
            )

        elif topic == "subscription_audit":
            monthly_savings = "$45"  # Default
            # Could calculate from subscription data if available
            return CHART_GENERATOR.generate_subscription_audit(
                monthly_savings=monthly_savings
            )

        elif topic == "automation":
            savings_pct = 10  # Default recommendation
            return CHART_GENERATOR.generate_automated_savings_flow(
                savings_pct=savings_pct
            )

        else:
            return {"success": False, "error": f"Unsupported topic: {topic}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
