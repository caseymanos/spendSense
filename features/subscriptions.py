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
    # Normalize to day-level to avoid time-of-day edge effects
    txns = transactions_df.copy()
    txns['date'] = pd.to_datetime(txns['date']).dt.normalize()

    # Filter to user's transactions in window (compare at day precision)
    cutoff_date = pd.Timestamp(datetime.now().date() - timedelta(days=window_days))
    user_txns = txns[
        (txns['user_id'] == user_id) &
        (txns['date'] >= cutoff_date) &
        (txns['amount'] > 0)  # Only debits (positive = money out)
    ].copy()

    # Analyze recurring cadence within the last lookback horizon (sliding window)
    lookback_days = SUBSCRIPTION_DETECTION['lookback_days']
    analysis_horizon = min(lookback_days, window_days)
    analysis_cutoff = pd.Timestamp(datetime.now().date() - timedelta(days=analysis_horizon))
    txns_for_detection = user_txns[user_txns['date'] >= analysis_cutoff].copy()

    if len(user_txns) == 0:
        return {
            'recurring_count': 0,
            'monthly_recurring_spend': 0.0,
            'subscription_share_pct': 0.0,
            'recurring_merchants': []
        }

    # Group by merchant and analyze patterns
    merchant_groups = txns_for_detection.groupby('merchant_name').agg({
        'amount': ['count', 'mean', 'std'],
        'date': ['min', 'max']
    }).reset_index()

    merchant_groups.columns = ['merchant_name', 'count', 'mean_amount', 'std_amount', 'first_date', 'last_date']

    # Detect recurring merchants
    recurring_merchants = []
    min_occurrences = SUBSCRIPTION_DETECTION['min_occurrences']
    amount_variance_pct = SUBSCRIPTION_DETECTION['amount_variance_pct']

    for _, row in merchant_groups.iterrows():
        # Need minimum occurrences
        if row['count'] < min_occurrences:
            continue

        # Check pattern span and honor lookback without breaking short windows
        days_span = (row['last_date'] - row['first_date']).days
        max_allowed_span = analysis_horizon
        # If occurrences are spread wider than allowed horizon, skip
        if days_span > max_allowed_span:
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
    signals_180d = detect_subscriptions(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["long_term_days"]
    )

    # For 30d, compute spend/share for the merchants detected as recurring in 180d
    signals_30d = detect_subscriptions(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["short_term_days"]
    )

    try:
        from datetime import datetime, timedelta
        cutoff_30 = pd.Timestamp(datetime.now().date() - timedelta(days=TIME_WINDOWS["short_term_days"]))
        txns2 = transactions_df.copy()
        txns2['date'] = pd.to_datetime(txns2['date']).dt.normalize()
        user_30 = txns2[(txns2['user_id'] == user_id) & (txns2['date'] >= cutoff_30)].copy()
        rec_merchants = signals_180d.get('recurring_merchants', [])
        if rec_merchants:
            rec_txns_30 = user_30[user_30['merchant_name'].isin(rec_merchants)]
            total_rec_spend_30 = float(rec_txns_30[rec_txns_30['amount'] > 0]['amount'].sum())
            total_spend_30 = float(user_30[user_30['amount'] > 0]['amount'].sum())
            signals_30d['monthly_recurring_spend'] = round(total_rec_spend_30, 2)
            signals_30d['subscription_share_pct'] = round((total_rec_spend_30 / total_spend_30 * 100) if total_spend_30 > 0 else 0.0, 2)
    except Exception:
        # Fall back silently if any issue arises
        pass

    return {
        '30d': signals_30d,
        '180d': signals_180d
    }
