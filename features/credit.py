"""
Credit utilization detection module for SpendSense MVP V2.
Analyzes credit card usage patterns and liability status.
"""

import pandas as pd
from typing import Dict, List

from ingest.constants import CREDIT_UTILIZATION_FLAGS
from ingest.schemas import AccountType, AccountSubtype


def calculate_credit_signals(
    accounts_df: pd.DataFrame,
    liabilities_df: pd.DataFrame,
    user_id: str
) -> Dict[str, any]:
    """
    Calculate credit-related behavioral signals.

    Credit utilization and liability status are point-in-time, not time-windowed.

    Args:
        accounts_df: DataFrame with account data
        liabilities_df: DataFrame with liability data
        user_id: User ID to analyze

    Returns:
        Dictionary containing:
        - max_utilization_pct: Highest utilization across all cards
        - avg_utilization_pct: Average utilization across all cards
        - flag_30: Boolean, any card ≥30% utilized
        - flag_50: Boolean, any card ≥50% utilized
        - flag_80: Boolean, any card ≥80% utilized
        - min_payment_only: Boolean, making only minimum payments
        - has_interest: Boolean, any interest charges present
        - is_overdue: Boolean, any overdue amounts
        - num_credit_cards: Number of credit cards
        - utilization_by_card: List of per-card utilization details
    """
    # Get user's credit card accounts
    credit_cards = accounts_df[
        (accounts_df['user_id'] == user_id) &
        (accounts_df['account_type'] == AccountType.CREDIT.value) &
        (accounts_df['account_subtype'] == AccountSubtype.CREDIT_CARD.value)
    ].copy()

    if len(credit_cards) == 0:
        return {
            'max_utilization_pct': 0.0,
            'avg_utilization_pct': 0.0,
            'flag_30': False,
            'flag_50': False,
            'flag_80': False,
            'min_payment_only': False,
            'has_interest': False,
            'is_overdue': False,
            'num_credit_cards': 0,
            'utilization_by_card': []
        }

    # Calculate utilization for each card
    utilizations = []
    utilization_details = []

    for _, card in credit_cards.iterrows():
        if card['balance_limit'] and card['balance_limit'] > 0:
            utilization = (card['balance_current'] / card['balance_limit']) * 100
            utilizations.append(utilization)
            utilization_details.append({
                'account_id': card['account_id'],
                'mask': card['mask'],
                'balance': card['balance_current'],
                'limit': card['balance_limit'],
                'utilization_pct': round(utilization, 2)
            })

    # Calculate aggregate metrics
    if len(utilizations) > 0:
        max_utilization = max(utilizations)
        avg_utilization = sum(utilizations) / len(utilizations)
    else:
        max_utilization = 0.0
        avg_utilization = 0.0

    # Check threshold flags (thresholds are already in percentage form: 30.0 = 30%)
    flag_30 = max_utilization >= CREDIT_UTILIZATION_FLAGS['warning_threshold']
    flag_50 = max_utilization >= CREDIT_UTILIZATION_FLAGS['high_threshold']
    flag_80 = max_utilization >= CREDIT_UTILIZATION_FLAGS['critical_threshold']

    # Check liabilities for minimum payment and interest patterns
    credit_account_ids = credit_cards['account_id'].tolist()
    user_liabilities = liabilities_df[
        liabilities_df['account_id'].isin(credit_account_ids)
    ]

    min_payment_only = False
    has_interest = False
    is_overdue = False

    if len(user_liabilities) > 0:
        # Check for minimum payment only pattern
        # If last payment ≈ minimum payment (within 5% tolerance)
        for _, liab in user_liabilities.iterrows():
            if pd.notna(liab['last_payment_amount']) and pd.notna(liab['minimum_payment']):
                if liab['minimum_payment'] > 0:
                    payment_ratio = liab['last_payment_amount'] / liab['minimum_payment']
                    if 0.95 <= payment_ratio <= 1.05:  # Within 5% of minimum
                        min_payment_only = True

            # Check for interest (APR > 0 indicates interest accrual)
            if liab['apr'] > 0:
                has_interest = True

            # Check for overdue status
            if liab['is_overdue']:
                is_overdue = True

    return {
        'max_utilization_pct': round(max_utilization, 2),
        'avg_utilization_pct': round(avg_utilization, 2),
        'flag_30': flag_30,
        'flag_50': flag_50,
        'flag_80': flag_80,
        'min_payment_only': min_payment_only,
        'has_interest': has_interest,
        'is_overdue': is_overdue,
        'num_credit_cards': len(credit_cards),
        'utilization_by_card': utilization_details
    }


def compute_credit_signals(
    accounts_df: pd.DataFrame,
    liabilities_df: pd.DataFrame,
    user_id: str
) -> Dict[str, any]:
    """
    Compute credit signals (point-in-time, no time windows needed).

    Args:
        accounts_df: DataFrame with account data
        liabilities_df: DataFrame with liability data
        user_id: User ID to analyze

    Returns:
        Dictionary with credit signals
    """
    signals = calculate_credit_signals(accounts_df, liabilities_df, user_id)

    # Return as 'current' since credit utilization is point-in-time
    return {
        'current': signals
    }
