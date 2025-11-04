"""
Subscription detection module for SpendSense MVP V2.
Identifies recurring merchants and calculates subscription metrics.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from ingest.constants import SUBSCRIPTION_DETECTION, TIME_WINDOWS


def detect_subscriptions(
    transactions_df: pd.DataFrame,
    user_id: str,
    window_days: int = TIME_WINDOWS["long_term_days"]
) -> Dict[str, any]:
    """
    Detect recurring subscription patterns for a user.

    Args:
        transactions_df: DataFrame with transaction data
        user_id: User ID to analyze
        window_days: Time window in days (30 or 180)

    Returns:
        Dictionary containing:
        - recurring_count: Number of recurring merchants
        - monthly_recurring_spend: Average monthly spend on subscriptions
        - subscription_share_pct: Percentage of total spend on subscriptions
        - recurring_merchants: List of detected recurring merchant names
    """
    # Filter to user's transactions in window
    cutoff_date = datetime.now() - timedelta(days=window_days)
    user_txns = transactions_df[
        (transactions_df['user_id'] == user_id) &
        (transactions_df['date'] >= cutoff_date) &
        (transactions_df['amount'] > 0)  # Only debits (positive = money out)
    ].copy()

    if len(user_txns) == 0:
        return {
            'recurring_count': 0,
            'monthly_recurring_spend': 0.0,
            'subscription_share_pct': 0.0,
            'recurring_merchants': []
        }

    # Group by merchant and analyze patterns
    merchant_groups = user_txns.groupby('merchant_name').agg({
        'amount': ['count', 'mean', 'std'],
        'date': ['min', 'max']
    }).reset_index()

    merchant_groups.columns = ['merchant_name', 'count', 'mean_amount', 'std_amount', 'first_date', 'last_date']

    # Detect recurring merchants
    recurring_merchants = []
    min_occurrences = SUBSCRIPTION_DETECTION['min_occurrences']
    amount_variance_pct = SUBSCRIPTION_DETECTION['amount_variance_pct']
    lookback_days = SUBSCRIPTION_DETECTION['lookback_days']

    for _, row in merchant_groups.iterrows():
        # Need minimum occurrences
        if row['count'] < min_occurrences:
            continue

        # Check if pattern spans long enough to be considered recurring
        days_span = (row['last_date'] - row['first_date']).days
        # Require at least 30 days of history to confirm recurring pattern
        min_span_days = 30  # At least 1 month of recurring behavior
        if days_span < min_span_days:
            continue

        # Amount should be relatively consistent (low variance)
        if pd.notna(row['std_amount']) and row['mean_amount'] > 0:
            variance_ratio = row['std_amount'] / row['mean_amount']
            if variance_ratio <= amount_variance_pct:
                recurring_merchants.append(row['merchant_name'])
        elif pd.isna(row['std_amount']) or row['std_amount'] == 0:
            # If std is NaN or 0 (all same amount), it's definitely recurring
            recurring_merchants.append(row['merchant_name'])

    # Calculate metrics
    if len(recurring_merchants) > 0:
        recurring_txns = user_txns[user_txns['merchant_name'].isin(recurring_merchants)]
        total_recurring_spend = recurring_txns['amount'].sum()

        # Calculate monthly average (normalize to 30 days)
        monthly_recurring_spend = total_recurring_spend * (30 / window_days)

        # Calculate share of total spend
        total_spend = user_txns['amount'].sum()
        subscription_share_pct = (total_recurring_spend / total_spend * 100) if total_spend > 0 else 0.0
    else:
        monthly_recurring_spend = 0.0
        subscription_share_pct = 0.0

    return {
        'recurring_count': len(recurring_merchants),
        'monthly_recurring_spend': round(monthly_recurring_spend, 2),
        'subscription_share_pct': round(subscription_share_pct, 2),
        'recurring_merchants': recurring_merchants
    }


def compute_subscription_signals(
    transactions_df: pd.DataFrame,
    user_id: str
) -> Dict[str, any]:
    """
    Compute subscription signals for both 30-day and 180-day windows.

    Args:
        transactions_df: DataFrame with transaction data
        user_id: User ID to analyze

    Returns:
        Dictionary with signals for both windows
    """
    signals_30d = detect_subscriptions(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["short_term_days"]
    )

    signals_180d = detect_subscriptions(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["long_term_days"]
    )

    return {
        '30d': signals_30d,
        '180d': signals_180d
    }
