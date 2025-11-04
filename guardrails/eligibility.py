"""
Eligibility Checking for SpendSense MVP V2

This module validates partner offer eligibility based on user financial profile.
Ensures users only see relevant, appropriate product recommendations.

Core Functions:
- check_product_eligibility(offer, user_context): Validate offer against rules
- filter_predatory_products(offers): Exclude predatory products
- check_existing_accounts(offer, user_context): Prevent duplicate offers
- apply_all_filters(offers, user_context): Run all eligibility checks

Design Principles:
- Don't recommend products user isn't eligible for
- Check minimum income/credit requirements
- Filter based on existing accounts
- Avoid harmful/predatory products
- Provide clear exclusion reasons for audit trail

Compliance:
- Implements PRD Part 2, Section 8.2: Eligibility Guardrails
- Uses ELIGIBILITY_RULES and PREDATORY_PRODUCTS from constants
"""

from typing import List, Dict, Any, Tuple

from ingest.constants import ELIGIBILITY_RULES, PREDATORY_PRODUCTS


# Income tier ordering for comparison
INCOME_TIER_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def check_product_eligibility(offer: Dict[str, Any], user_context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if a user is eligible for a specific partner offer.

    Args:
        offer: Partner offer dict with:
            - product_type: Type of product (e.g., "savings_account", "credit_card")
            - min_income_tier: Minimum income requirement (if applicable)
            - (other fields)
        user_context: User context dict with:
            - income_tier: User's income tier
            - signals: Behavioral signals (utilization, etc.)
            - existing_account_types: Dict of account type counts
            - (other fields)

    Returns:
        Tuple of:
        - eligible: True if eligible, False otherwise
        - reason: Explanation for decision

    Example:
        >>> offer = {"product_type": "credit_card", "title": "Balance Transfer Card"}
        >>> context = {"income_tier": "low", "signals": {"credit_utilization_30d": 0.85}}
        >>> eligible, reason = check_product_eligibility(offer, context)
        >>> eligible
        False
        >>> reason
        'Credit utilization too high (85%)'
    """
    product_type = offer.get("product_type", "unknown")
    user_income_tier = user_context.get("income_tier", "low")
    signals = user_context.get("signals", {})
    existing_accounts = user_context.get("existing_account_types", {})

    # Get eligibility rules for this product type
    rules = ELIGIBILITY_RULES.get(product_type, {})

    if not rules:
        # No specific rules for this product type - allow by default
        return True, "No specific eligibility restrictions"

    # Check minimum income tier
    if "min_income_tier" in rules:
        required_tier = rules["min_income_tier"]
        user_tier_rank = INCOME_TIER_ORDER.get(user_income_tier, 1)
        required_tier_rank = INCOME_TIER_ORDER.get(required_tier, 1)

        if user_tier_rank < required_tier_rank:
            return False, f"Income tier {user_income_tier} below required {required_tier}"

    # Check maximum existing accounts (for savings accounts)
    if "max_existing_savings" in rules:
        max_allowed = rules["max_existing_savings"]
        # Count savings-type accounts
        savings_count = existing_accounts.get("savings", 0)
        savings_count += existing_accounts.get("money_market", 0)
        savings_count += existing_accounts.get("hsa", 0)

        if savings_count >= max_allowed:
            return False, f"Already has {savings_count} savings accounts (max {max_allowed})"

    # Check maximum credit utilization (for credit cards)
    if "max_credit_utilization" in rules:
        max_utilization = rules["max_credit_utilization"]
        # Check both 30-day and 180-day utilization
        util_30d = signals.get("credit_utilization_30d", 0)
        util_180d = signals.get("credit_utilization_180d", 0)
        current_util = max(util_30d, util_180d)

        if current_util > max_utilization:
            return False, f"Credit utilization too high ({int(current_util * 100)}%)"

    # All checks passed
    return True, "Eligible"


def filter_predatory_products(offers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove predatory products from offer list.

    Args:
        offers: List of partner offer dicts

    Returns:
        Tuple of:
        - Filtered list of safe offers
        - List of blocked offers with reasons

    Example:
        >>> offers = [
        ...     {"product_type": "payday_loan", "title": "Quick Cash"},
        ...     {"product_type": "savings_account", "title": "HYSA"}
        ... ]
        >>> safe, blocked = filter_predatory_products(offers)
        >>> len(safe)
        1
        >>> blocked[0]['reason']
        'Predatory product type: payday_loan'
    """
    safe_offers = []
    blocked_offers = []

    for offer in offers:
        product_type = offer.get("product_type", "unknown")

        if product_type in PREDATORY_PRODUCTS:
            blocked_offers.append({
                "offer": offer,
                "reason": f"Predatory product type: {product_type}",
                "blocked_at": "predatory_filter",
            })
        else:
            safe_offers.append(offer)

    return safe_offers, blocked_offers


def check_existing_accounts(offer: Dict[str, Any], user_context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if user already owns this type of product.

    Args:
        offer: Partner offer dict with product_type
        user_context: User context dict with existing_account_types

    Returns:
        Tuple of:
        - should_offer: True if user doesn't have this product, False otherwise
        - reason: Explanation for decision

    Example:
        >>> offer = {"product_type": "savings_account", "title": "Marcus HYSA"}
        >>> context = {"existing_account_types": {"savings": 2}}
        >>> should_offer, reason = check_existing_accounts(offer, context)
        >>> should_offer
        False
        >>> reason
        'User already has savings account(s)'
    """
    product_type = offer.get("product_type", "unknown")
    existing_accounts = user_context.get("existing_account_types", {})

    # Map product types to account types
    product_to_account_mapping = {
        "savings_account": ["savings", "money_market", "hsa"],
        "credit_card": ["credit_card", "credit"],
        "checking_account": ["checking", "depository"],
        "budgeting_app": [],  # Apps don't map to account types
        "subscription_management": [],  # Apps don't map to account types
    }

    account_types_to_check = product_to_account_mapping.get(product_type, [])

    if not account_types_to_check:
        # Product type doesn't conflict with existing accounts (e.g., apps, services)
        return True, "Product type doesn't conflict with existing accounts"

    # Check if user has any of these account types
    for account_type in account_types_to_check:
        count = existing_accounts.get(account_type, 0)
        if count > 0:
            return False, f"User already has {account_type} account(s)"

    return True, "User doesn't have this product type"


def apply_all_filters(offers: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all eligibility filters to a list of offers.

    Args:
        offers: List of partner offer dicts
        user_context: User context dict

    Returns:
        Dictionary with:
        - eligible_offers: List of offers that passed all checks
        - blocked_offers: List of dicts with offer and blocking reason
        - total_offers: Original count
        - eligible_count: Count of eligible offers
        - blocked_count: Count of blocked offers
        - filters_applied: List of filter names applied

    Example:
        >>> offers = [{"product_type": "savings_account", "title": "HYSA"}]
        >>> context = {"income_tier": "medium", "existing_account_types": {}}
        >>> result = apply_all_filters(offers, context)
        >>> result['eligible_count']
        1
    """
    total_offers = len(offers)
    eligible_offers = []
    blocked_offers = []

    # Filter 1: Remove predatory products
    safe_offers, predatory_blocked = filter_predatory_products(offers)
    blocked_offers.extend(predatory_blocked)

    # Filter 2: Check eligibility rules and existing accounts
    for offer in safe_offers:
        # Check product eligibility (income tier, utilization, etc.)
        eligible, reason = check_product_eligibility(offer, user_context)

        if not eligible:
            blocked_offers.append({
                "offer": offer,
                "reason": reason,
                "blocked_at": "product_eligibility",
            })
            continue

        # Check existing accounts
        should_offer, account_reason = check_existing_accounts(offer, user_context)

        if not should_offer:
            blocked_offers.append({
                "offer": offer,
                "reason": account_reason,
                "blocked_at": "existing_accounts",
            })
            continue

        # Passed all filters
        eligible_offers.append(offer)

    return {
        "eligible_offers": eligible_offers,
        "blocked_offers": blocked_offers,
        "total_offers": total_offers,
        "eligible_count": len(eligible_offers),
        "blocked_count": len(blocked_offers),
        "filters_applied": [
            "predatory_products",
            "product_eligibility",
            "existing_accounts",
        ],
    }


def get_eligibility_summary(user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of user's eligibility status for common product types.

    Args:
        user_context: User context dict

    Returns:
        Dictionary mapping product types to eligibility status

    Example:
        >>> context = {"income_tier": "high", "existing_account_types": {"savings": 1}}
        >>> summary = get_eligibility_summary(context)
        >>> summary['savings_account']['eligible']
        False
        >>> summary['credit_card']['eligible']
        True
    """
    common_products = [
        "savings_account",
        "credit_card",
        "budgeting_app",
    ]

    summary = {}

    for product_type in common_products:
        # Create a dummy offer to check eligibility
        dummy_offer = {"product_type": product_type, "title": f"Sample {product_type}"}

        # Check product eligibility
        product_eligible, product_reason = check_product_eligibility(dummy_offer, user_context)

        # Check existing accounts
        account_eligible, account_reason = check_existing_accounts(dummy_offer, user_context)

        # Combine results
        overall_eligible = product_eligible and account_eligible
        reasons = []
        if not product_eligible:
            reasons.append(product_reason)
        if not account_eligible:
            reasons.append(account_reason)

        summary[product_type] = {
            "eligible": overall_eligible,
            "reasons": reasons if not overall_eligible else ["Eligible"],
        }

    return summary
