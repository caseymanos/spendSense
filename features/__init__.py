"""
Feature pipeline orchestrator for SpendSense MVP V2.
Coordinates all behavioral signal detection modules.
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from features.subscriptions import compute_subscription_signals
from features.savings import compute_savings_signals
from features.credit import compute_credit_signals
from features.income import compute_income_signals
from ingest.constants import TRACE_CONFIG


def load_data(db_path: str = "data/users.sqlite", parquet_path: str = "data/transactions.parquet"):
    """
    Load data from SQLite and Parquet files.

    Args:
        db_path: Path to SQLite database
        parquet_path: Path to Parquet file with transactions

    Returns:
        Tuple of (transactions_df, accounts_df, liabilities_df, users_df)
    """
    # Load transactions from Parquet
    transactions_df = pd.read_parquet(parquet_path)

    # Ensure date column is datetime
    if 'date' in transactions_df.columns:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    # Load accounts and liabilities from SQLite
    conn = sqlite3.connect(db_path)

    accounts_df = pd.read_sql_query("SELECT * FROM accounts", conn)
    liabilities_df = pd.read_sql_query("SELECT * FROM liabilities", conn)
    users_df = pd.read_sql_query("SELECT user_id, consent_granted FROM users", conn)

    conn.close()

    return transactions_df, accounts_df, liabilities_df, users_df


def _detect_interest_charges(transactions_df: pd.DataFrame, accounts_df: pd.DataFrame, user_id: str, window_days: int = 60) -> Dict[str, float | bool]:
    """
    Detect posted interest/finance charges on the user's credit accounts.

    Heuristic: look back `window_days`, filter to user's credit account_ids and
    debits whose merchant/category suggest interest/finance charges.

    Returns a dict with:
    - present: bool
    - amount_sum: float (sum over window)
    """
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=window_days)

    # Identify user's credit account_ids
    credit_ids = (
        accounts_df[
            (accounts_df['user_id'] == user_id)
        ]
        .query("account_type == 'credit' and account_subtype == 'credit card'")
        .get('account_id', pd.Series(dtype=str))
        .tolist()
    )

    if len(credit_ids) == 0 or 'merchant_name' not in transactions_df.columns:
        return {"present": False, "amount_sum": 0.0}

    user_txns = transactions_df[
        (transactions_df['user_id'] == user_id) &
        (transactions_df['date'] >= cutoff_date) &
        (transactions_df['account_id'].isin(credit_ids)) &
        (transactions_df['amount'] > 0)  # Debits (charges)
    ].copy()

    if len(user_txns) == 0:
        return {"present": False, "amount_sum": 0.0}

    # Match by merchant text or category hints
    text = user_txns['merchant_name'].astype('string').str.lower()
    cat = user_txns.get('personal_finance_category', pd.Series([], dtype='string')).astype('string').str.lower()

    interest_mask = (
        text.str.contains('interest', na=False) |
        text.str.contains('finance charge', na=False) |
        text.str.contains('finance fee', na=False) |
        cat.str.contains('fee', na=False) |
        cat.str.contains('interest', na=False)
    )

    hits = user_txns[interest_mask]
    amount_sum = float(hits['amount'].sum()) if len(hits) > 0 else 0.0
    return {"present": amount_sum > 0, "amount_sum": amount_sum}


def compute_all_signals(user_id: str, transactions_df: pd.DataFrame, accounts_df: pd.DataFrame, liabilities_df: pd.DataFrame) -> Dict:
    """
    Compute all behavioral signals for a single user.

    Args:
        user_id: User ID to analyze
        transactions_df: DataFrame with transaction data
        accounts_df: DataFrame with account data
        liabilities_df: DataFrame with liability data

    Returns:
        Dictionary containing all signals
    """
    # Add user_id to transactions if not present (join from accounts)
    if 'user_id' not in transactions_df.columns:
        account_user_map = accounts_df[['account_id', 'user_id']].drop_duplicates()
        transactions_df = transactions_df.merge(account_user_map, on='account_id', how='left')

    # Compute signals from each module
    subscription_signals = compute_subscription_signals(transactions_df, user_id)
    savings_signals = compute_savings_signals(transactions_df, accounts_df, user_id)
    credit_signals = compute_credit_signals(accounts_df, liabilities_df, user_id)

    # Augment credit signals with posted interest detection (spec-accurate)
    interest = _detect_interest_charges(transactions_df, accounts_df, user_id)
    credit_signals.setdefault('current', {})['interest_charges_present'] = bool(interest['present'])
    credit_signals['current']['interest_charges_amount_60d'] = float(interest['amount_sum'])
    income_signals = compute_income_signals(transactions_df, user_id)

    return {
        'user_id': user_id,
        'subscriptions': subscription_signals,
        'savings': savings_signals,
        'credit': credit_signals,
        'income': income_signals,
        'timestamp': datetime.now().isoformat()
    }


def save_trace(user_id: str, signals: Dict, trace_dir: str = "docs/traces"):
    """
    Save per-user decision trace to JSON file.

    Args:
        user_id: User ID
        signals: Dictionary of all signals
        trace_dir: Directory to save trace files
    """
    trace_path = Path(trace_dir)
    trace_path.mkdir(parents=True, exist_ok=True)

    trace_file = trace_path / f"{user_id}.json"

    # Create trace structure
    trace = {
        'user_id': user_id,
        'timestamp': signals['timestamp'],
        'phase': 'behavioral_signals',
        'signals': {
            'subscriptions': signals['subscriptions'],
            'savings': signals['savings'],
            'credit': signals['credit'],
            'income': signals['income']
        }
    }

    with open(trace_file, 'w') as f:
        json.dump(trace, f, indent=2)


def flatten_signals_for_parquet(signals: Dict) -> Dict:
    """
    Flatten nested signal structure for Parquet storage.

    Args:
        signals: Nested signals dictionary

    Returns:
        Flattened dictionary with column-friendly keys
    """
    flat = {'user_id': signals['user_id']}

    # Subscription signals
    for window in ['30d', '180d']:
        prefix = f'sub_{window}_'
        sub_signals = signals['subscriptions'].get(window, {})
        flat[f'{prefix}recurring_count'] = sub_signals.get('recurring_count', 0)
        flat[f'{prefix}monthly_spend'] = sub_signals.get('monthly_recurring_spend', 0.0)
        flat[f'{prefix}share_pct'] = sub_signals.get('subscription_share_pct', 0.0)

    # Savings signals
    for window in ['30d', '180d']:
        prefix = f'sav_{window}_'
        sav_signals = signals['savings'].get(window, {})
        flat[f'{prefix}net_inflow'] = sav_signals.get('net_inflow', 0.0)
        flat[f'{prefix}growth_rate_pct'] = sav_signals.get('growth_rate_pct', 0.0)
        flat[f'{prefix}emergency_fund_months'] = sav_signals.get('emergency_fund_months', 0.0)
        flat[f'{prefix}balance'] = sav_signals.get('savings_balance', 0.0)

    # Credit signals (current only)
    credit_signals = signals['credit'].get('current', {})
    flat['credit_max_util_pct'] = credit_signals.get('max_utilization_pct', 0.0)
    flat['credit_avg_util_pct'] = credit_signals.get('avg_utilization_pct', 0.0)
    flat['credit_flag_30'] = credit_signals.get('flag_30', False)
    flat['credit_flag_50'] = credit_signals.get('flag_50', False)
    flat['credit_flag_80'] = credit_signals.get('flag_80', False)
    flat['credit_min_payment_only'] = credit_signals.get('min_payment_only', False)
    flat['credit_has_interest'] = credit_signals.get('has_interest', False)
    flat['credit_interest_charges'] = credit_signals.get('interest_charges_present', False)
    flat['credit_is_overdue'] = credit_signals.get('is_overdue', False)
    flat['credit_num_cards'] = credit_signals.get('num_credit_cards', 0)

    # Income signals
    for window in ['30d', '180d']:
        prefix = f'inc_{window}_'
        inc_signals = signals['income'].get(window, {})
        flat[f'{prefix}median_pay_gap_days'] = inc_signals.get('median_pay_gap_days', 0)
        flat[f'{prefix}variability'] = inc_signals.get('income_variability', 0.0)
        flat[f'{prefix}cash_buffer_months'] = inc_signals.get('cash_buffer_months', 0.0)
        flat[f'{prefix}num_paychecks'] = inc_signals.get('num_paychecks', 0)
        flat[f'{prefix}avg_paycheck'] = inc_signals.get('avg_paycheck', 0.0)

    return flat


def run_feature_pipeline(
    db_path: str = "data/users.sqlite",
    parquet_path: str = "data/transactions.parquet",
    output_path: str = "features/signals.parquet",
    trace_dir: str = "docs/traces"
) -> pd.DataFrame:
    """
    Run the complete feature detection pipeline for all users.

    Args:
        db_path: Path to SQLite database
        parquet_path: Path to transactions Parquet file
        output_path: Path to save output signals Parquet
        trace_dir: Directory to save trace JSON files

    Returns:
        DataFrame with all user signals
    """
    print("Loading data...")
    transactions_df, accounts_df, liabilities_df, users_df = load_data(db_path, parquet_path)

    # Get list of users with consent
    consented_users = users_df[users_df['consent_granted'] == True]['user_id'].tolist()
    all_users = users_df['user_id'].tolist()

    print(f"Found {len(all_users)} total users, {len(consented_users)} with consent")
    print("Note: Computing signals for ALL users for testing; consent enforcement in PR #5")

    # Compute signals for all users
    all_signals = []
    for i, user_id in enumerate(all_users, 1):
        if i % 10 == 0 or i == len(all_users):
            print(f"Processing user {i}/{len(all_users)}...")

        signals = compute_all_signals(user_id, transactions_df, accounts_df, liabilities_df)
        all_signals.append(signals)

        # Save trace
        save_trace(user_id, signals, trace_dir)

    # Flatten signals for Parquet
    print("Flattening signals for Parquet storage...")
    flattened_signals = [flatten_signals_for_parquet(s) for s in all_signals]
    signals_df = pd.DataFrame(flattened_signals)

    # Save to Parquet
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    signals_df.to_parquet(output_path, index=False)
    print(f" Saved signals to {output_path}")
    print(f" Saved {len(all_signals)} trace files to {trace_dir}/")

    return signals_df


if __name__ == "__main__":
    # Run the pipeline when module is executed directly
    signals_df = run_feature_pipeline()
    print("\n Feature pipeline complete!")
    print(f"Generated signals for {len(signals_df)} users")
    print(f"\nSignal columns: {list(signals_df.columns)}")
    print(f"\nSample signals:\n{signals_df.head()}")
