"""
Income stability detection module for SpendSense MVP V2.
Analyzes payroll patterns and cash flow buffer.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

from ingest.constants import INCOME_DETECTION, TIME_WINDOWS


def detect_income_signals(
    transactions_df: pd.DataFrame,
    user_id: str,
    window_days: int = TIME_WINDOWS["long_term_days"]
) -> Dict[str, any]:
    """
    Detect income stability patterns from payroll transactions.

    Args:
        transactions_df: DataFrame with transaction data
        user_id: User ID to analyze
        window_days: Time window in days (30 or 180)

    Returns:
        Dictionary containing:
        - median_pay_gap_days: Median days between paychecks
        - income_variability: Standard deviation of paycheck amounts
        - cash_buffer_months: Months of expenses covered by checking balance
        - pay_frequency: Detected pay frequency (weekly, biweekly, monthly, variable)
        - num_paychecks: Number of paychecks detected
        - avg_paycheck: Average paycheck amount
    """
    # Filter to user's transactions in window
    cutoff_date = datetime.now() - timedelta(days=window_days)
    user_txns = transactions_df[
        (transactions_df['user_id'] == user_id) &
        (transactions_df['date'] >= cutoff_date)
    ].copy()

    if len(user_txns) == 0:
        return {
            'median_pay_gap_days': 0,
            'income_variability': 0.0,
            'cash_buffer_months': 0.0,
            'pay_frequency': 'unknown',
            'num_paychecks': 0,
            'avg_paycheck': 0.0
        }

    # Detect payroll transactions (negative amounts = credits/deposits)
    payroll_keywords = INCOME_DETECTION['payroll_keywords']

    # Create case-insensitive pattern for payroll detection
    payroll_pattern = '|'.join(payroll_keywords)
    payroll_txns = user_txns[
        (user_txns['amount'] < 0) &  # Credits only (money in)
        (user_txns['merchant_name'].str.contains(payroll_pattern, case=False, na=False))
    ].copy()

    # Also check personal_finance_category for income indicators
    income_category_pattern = 'INCOME|TRANSFER_IN'
    income_txns = user_txns[
        (user_txns['amount'] < 0) &  # Credits only
        (user_txns['personal_finance_category'].str.contains(income_category_pattern, case=False, na=False))
    ]

    # Combine both detection methods
    payroll_txns = pd.concat([payroll_txns, income_txns]).drop_duplicates(subset=['transaction_id'])
    payroll_txns = payroll_txns.sort_values('date')

    min_occurrences = INCOME_DETECTION['min_income_occurrences']

    if len(payroll_txns) < min_occurrences:
        return {
            'median_pay_gap_days': 0,
            'income_variability': 0.0,
            'cash_buffer_months': 0.0,
            'pay_frequency': 'unknown',
            'num_paychecks': len(payroll_txns),
            'avg_paycheck': 0.0
        }

    # Calculate pay gaps (days between paychecks)
    pay_dates = payroll_txns['date'].tolist()
    pay_gaps = []
    for i in range(1, len(pay_dates)):
        gap = (pay_dates[i] - pay_dates[i-1]).days
        pay_gaps.append(gap)

    median_pay_gap = int(np.median(pay_gaps)) if len(pay_gaps) > 0 else 0

    # Detect pay frequency based on median gap
    tolerance = INCOME_DETECTION['frequency_tolerance_days']
    if 7 - tolerance <= median_pay_gap <= 7 + tolerance:
        pay_frequency = 'weekly'
    elif 14 - tolerance <= median_pay_gap <= 14 + tolerance:
        pay_frequency = 'biweekly'
    elif 28 - tolerance <= median_pay_gap <= 31 + tolerance:
        pay_frequency = 'monthly'
    else:
        pay_frequency = 'variable'

    # Calculate income variability (coefficient of variation)
    paycheck_amounts = payroll_txns['amount'].abs().tolist()  # Convert to positive
    avg_paycheck = np.mean(paycheck_amounts)
    std_paycheck = np.std(paycheck_amounts)
    income_variability = (std_paycheck / avg_paycheck) if avg_paycheck > 0 else 0.0

    # Calculate cash buffer
    # Get user's checking account balance and monthly expenses
    user_expenses = user_txns[user_txns['amount'] > 0]  # Debits only
    if len(user_expenses) > 0:
        total_expenses = user_expenses['amount'].sum()
        avg_monthly_expenses = total_expenses * (30 / window_days)

        # Estimate checking balance from recent activity (simplified)
        # In real implementation, we'd query accounts table
        # For now, use total income - total expenses as proxy
        total_income = abs(payroll_txns['amount'].sum())
        estimated_balance = total_income - total_expenses

        cash_buffer_months = (estimated_balance / avg_monthly_expenses) if avg_monthly_expenses > 0 else 0.0
    else:
        cash_buffer_months = 0.0

    return {
        'median_pay_gap_days': median_pay_gap,
        'income_variability': round(income_variability, 4),
        'cash_buffer_months': round(cash_buffer_months, 2),
        'pay_frequency': pay_frequency,
        'num_paychecks': len(payroll_txns),
        'avg_paycheck': round(avg_paycheck, 2)
    }


def compute_income_signals(
    transactions_df: pd.DataFrame,
    user_id: str
) -> Dict[str, any]:
    """
    Compute income stability signals for both 30-day and 180-day windows.

    Args:
        transactions_df: DataFrame with transaction data
        user_id: User ID to analyze

    Returns:
        Dictionary with signals for both windows
    """
    signals_30d = detect_income_signals(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["short_term_days"]
    )

    signals_180d = detect_income_signals(
        transactions_df,
        user_id,
        window_days=TIME_WINDOWS["long_term_days"]
    )

    return {
        '30d': signals_30d,
        '180d': signals_180d
    }
