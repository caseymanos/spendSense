"""
Savings signal detection module for SpendSense MVP V2.
Analyzes savings account activity and emergency fund coverage.
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import Dict

from ingest.constants import SAVINGS_ANALYSIS, TIME_WINDOWS
from ingest.schemas import AccountType, AccountSubtype


def calculate_savings_signals(
    transactions_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    user_id: str,
    window_days: int = TIME_WINDOWS["long_term_days"]
) -> Dict[str, any]:
    """
    Calculate savings-related behavioral signals.

    Args:
        transactions_df: DataFrame with transaction data
        accounts_df: DataFrame with account data
        user_id: User ID to analyze
        window_days: Time window in days (30 or 180)

    Returns:
        Dictionary containing:
        - net_inflow: Net money flow into savings accounts
        - growth_rate_pct: Percentage growth in savings balance
        - emergency_fund_months: Months of expenses covered by savings
        - savings_balance: Current total savings balance
    """
    # Get user's savings accounts
    savings_accounts = accounts_df[
        (accounts_df['user_id'] == user_id) &
        (accounts_df['account_type'] == AccountType.DEPOSITORY.value) &
        (accounts_df['account_subtype'] == AccountSubtype.SAVINGS.value)
    ]

    if len(savings_accounts) == 0:
        return {
            'net_inflow': 0.0,
            'growth_rate_pct': 0.0,
            'emergency_fund_months': 0.0,
            'savings_balance': 0.0
        }

    # Current total savings balance
    current_savings = savings_accounts['balance_current'].sum()

    # Get transactions for savings accounts in window
    cutoff_date = datetime.now() - timedelta(days=window_days)
    savings_account_ids = savings_accounts['account_id'].tolist()

    savings_txns = transactions_df[
        (transactions_df['account_id'].isin(savings_account_ids)) &
        (transactions_df['date'] >= cutoff_date)
    ].copy()

    # Calculate net inflow (negative amounts = credits/deposits, positive = debits/withdrawals)
    # Net inflow = deposits - withdrawals = -credits - debits = -(credits + debits)
    # But in our schema: positive = debit, negative = credit
    # So net inflow = sum of negative amounts (credits) - sum of positive amounts (debits)
    if len(savings_txns) > 0:
        credits = savings_txns[savings_txns['amount'] < 0]['amount'].sum()  # negative values
        debits = savings_txns[savings_txns['amount'] > 0]['amount'].sum()    # positive values
        net_inflow = abs(credits) - debits  # Convert credits to positive, subtract debits
    else:
        net_inflow = 0.0

    # Calculate growth rate
    # Growth rate = (current - beginning) / beginning * 100
    # Estimate beginning balance: current - net_inflow
    beginning_balance = max(current_savings - net_inflow, 0.01)  # Avoid division by zero
    growth_rate_pct = ((current_savings - beginning_balance) / beginning_balance * 100) if beginning_balance > 0 else 0.0

    # Calculate emergency fund coverage
    # Get all user's debit transactions (expenses) to calculate average monthly spend
    user_debits = transactions_df[
        (transactions_df['user_id'] == user_id) &
        (transactions_df['amount'] > 0) &  # Debits only
        (transactions_df['date'] >= cutoff_date)
    ]

    if len(user_debits) > 0:
        total_expenses = user_debits['amount'].sum()
        avg_monthly_expenses = total_expenses * (30 / window_days)
        emergency_fund_months = current_savings / avg_monthly_expenses if avg_monthly_expenses > 0 else 0.0
    else:
        emergency_fund_months = 0.0

    return {
        'net_inflow': round(net_inflow, 2),
        'growth_rate_pct': round(growth_rate_pct, 2),
        'emergency_fund_months': round(emergency_fund_months, 2),
        'savings_balance': round(current_savings, 2)
    }


def compute_savings_signals(
    transactions_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    user_id: str
) -> Dict[str, any]:
    """
    Compute savings signals for both 30-day and 180-day windows.

    Args:
        transactions_df: DataFrame with transaction data
        accounts_df: DataFrame with account data
        user_id: User ID to analyze

    Returns:
        Dictionary with signals for both windows
    """
    signals_30d = calculate_savings_signals(
        transactions_df,
        accounts_df,
        user_id,
        window_days=TIME_WINDOWS["short_term_days"]
    )

    signals_180d = calculate_savings_signals(
        transactions_df,
        accounts_df,
        user_id,
        window_days=TIME_WINDOWS["long_term_days"]
    )

    return {
        '30d': signals_30d,
        '180d': signals_180d
    }
