"""
Persona assignment module for SpendSense MVP V2.
Classifies users into behavioral personas based on detected signals.

Persona criteria based on spendSensePRDv3Part2.md Section 6.1.
"""

import pandas as pd
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Tuple
from pathlib import Path

from ingest.constants import PERSONA_THRESHOLDS, PERSONA_PRIORITY


def check_high_utilization(signals: pd.Series) -> Tuple[bool, Dict]:
    """
    Check if user meets High Utilization persona criteria.

    Criteria: Any card utilization ≥ 50% OR interest > 0 OR min-payment-only OR overdue = true

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (matches, criteria_met_dict)
    """
    criteria_met = {}

    # Check utilization ≥ 50%
    utilization = signals.get("credit_max_util_pct", 0)
    if utilization >= PERSONA_THRESHOLDS["High Utilization"]["utilization_threshold"]:
        criteria_met["high_utilization"] = float(utilization)

    # Interest charges posted > 0 (spec-accurate)
    interest_charges = signals.get("credit_interest_charges", False)
    if interest_charges:
        criteria_met["interest_charges"] = True

    # Check min-payment-only pattern
    min_payment_only = signals.get("credit_min_payment_only", False)
    if min_payment_only:
        criteria_met["min_payment_only"] = True

    # Check overdue status
    is_overdue = signals.get("credit_is_overdue", False)
    if is_overdue:
        criteria_met["is_overdue"] = True

    # Matches if ANY condition is true (OR logic)
    matches = len(criteria_met) > 0

    return matches, criteria_met


def check_variable_income(signals: pd.Series) -> Tuple[bool, Dict]:
    """
    Check if user meets Variable Income Budgeter persona criteria.

    Criteria: Median pay gap > 45 days AND cash-flow buffer < 1 month

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (matches, criteria_met_dict)
    """
    criteria_met = {}

    # Check median pay gap > 45 days (using 180-day window for long-term trend)
    median_pay_gap = signals.get("inc_180d_median_pay_gap_days", 0)
    if median_pay_gap > PERSONA_THRESHOLDS["Variable Income Budgeter"]["median_pay_gap_days"]:
        criteria_met["median_pay_gap_days"] = int(median_pay_gap)

    # Check cash buffer < 1 month (using 180-day window)
    cash_buffer = signals.get(
        "inc_180d_cash_buffer_months", 999
    )  # Default high to avoid false positives
    if cash_buffer < PERSONA_THRESHOLDS["Variable Income Budgeter"]["cash_buffer_months"]:
        criteria_met["cash_buffer_months"] = float(cash_buffer)

    # Matches if BOTH conditions are true (AND logic)
    matches = len(criteria_met) == 2

    return matches, criteria_met


def check_subscription_heavy(signals: pd.Series) -> Tuple[bool, Dict]:
    """
    Check if user meets Subscription-Heavy persona criteria.

    Criteria: Recurring merchants ≥ 3 AND (recurring spend ≥ $50 OR ≥ 10% of total spend)

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (matches, criteria_met_dict)
    """
    criteria_met = {}

    # Check recurring count ≥ 3 (detector enforces 90d cadence)
    recurring_count = signals.get("sub_180d_recurring_count", 0)
    if recurring_count >= PERSONA_THRESHOLDS["Subscription-Heavy"]["min_recurring_count"]:
        criteria_met["recurring_count"] = int(recurring_count)

    # Check 30d window for monthly spend/share per spec
    monthly_spend = signals.get("sub_30d_monthly_spend", signals.get("sub_180d_monthly_spend", 0))
    share_pct = signals.get("sub_30d_share_pct", signals.get("sub_180d_share_pct", 0))

    if monthly_spend >= PERSONA_THRESHOLDS["Subscription-Heavy"]["recurring_spend_min"]:
        criteria_met["monthly_spend"] = float(monthly_spend)

    if share_pct >= PERSONA_THRESHOLDS["Subscription-Heavy"]["recurring_spend_pct"]:
        criteria_met["share_pct"] = float(share_pct)

    # Matches if recurring_count ≥ 3 AND (spend ≥ $50 OR share ≥ 10%)
    has_count = recurring_count >= PERSONA_THRESHOLDS["Subscription-Heavy"]["min_recurring_count"]
    has_spend_or_share = (
        monthly_spend >= PERSONA_THRESHOLDS["Subscription-Heavy"]["recurring_spend_min"]
        or share_pct >= PERSONA_THRESHOLDS["Subscription-Heavy"]["recurring_spend_pct"]
    )

    matches = has_count and has_spend_or_share

    return matches, criteria_met


def check_savings_builder(signals: pd.Series) -> Tuple[bool, Dict]:
    """
    Check if user meets Savings Builder persona criteria.

    Criteria: Savings growth ≥ 2% OR net inflow ≥ $200 AND utilization < 30%

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (matches, criteria_met_dict)
    """
    criteria_met = {}

    # Check savings growth ≥ 2% (using 180-day window)
    growth_rate = signals.get("sav_180d_growth_rate_pct", 0)
    if growth_rate >= PERSONA_THRESHOLDS["Savings Builder"]["growth_rate_pct"]:
        criteria_met["growth_rate_pct"] = float(growth_rate)

    # Check net inflow ≥ $200
    net_inflow = signals.get("sav_180d_net_inflow", 0)
    if net_inflow >= PERSONA_THRESHOLDS["Savings Builder"]["net_inflow_min"]:
        criteria_met["net_inflow"] = float(net_inflow)

    # Check utilization < 30% (required for both OR branches)
    utilization = signals.get("credit_max_util_pct", 100)  # Default high to avoid false positives
    utilization_ok = utilization < PERSONA_THRESHOLDS["Savings Builder"]["max_utilization"]

    if utilization_ok:
        criteria_met["low_utilization"] = float(utilization)

    # Matches if (growth ≥ 2% OR inflow ≥ $200) AND utilization < 30%
    has_savings_metric = (
        growth_rate >= PERSONA_THRESHOLDS["Savings Builder"]["growth_rate_pct"]
        or net_inflow >= PERSONA_THRESHOLDS["Savings Builder"]["net_inflow_min"]
    )

    matches = has_savings_metric and utilization_ok

    return matches, criteria_met


def check_cash_flow_optimizer(signals: pd.Series) -> Tuple[bool, Dict]:
    """
    Check if user meets Cash Flow Optimizer persona criteria.

    Criteria: Cash buffer < 2 months AND (growth rate < 1% OR net inflow < $100)
              AND pay gap ≤ 45 days (stable income)

    This persona captures users with spending > income patterns who have:
    - Stable income (not variable income issues)
    - Low savings accumulation despite stable income
    - Cash flow management challenges

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (matches, criteria_met_dict)
    """
    criteria_met = {}

    # Check cash buffer < 2 months (using 180-day window)
    cash_buffer = signals.get("inc_180d_cash_buffer_months", 999)  # Default high to avoid false positives
    if cash_buffer < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_cash_buffer_months"]:
        criteria_met["cash_buffer_months"] = float(cash_buffer)

    # Check savings growth < 1% (using 180-day window)
    growth_rate = signals.get("sav_180d_growth_rate_pct", 0)
    if growth_rate < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_growth_rate_pct"]:
        criteria_met["low_growth_rate_pct"] = float(growth_rate)

    # Check net inflow < $100 (using 180-day window)
    net_inflow = signals.get("sav_180d_net_inflow", 0)
    if net_inflow < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_net_inflow"]:
        criteria_met["low_net_inflow"] = float(net_inflow)

    # Check pay gap ≤ 45 days (stable income - differentiates from Variable Income)
    median_pay_gap = signals.get("inc_180d_median_pay_gap_days", 0)
    if median_pay_gap > 0 and median_pay_gap <= PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_pay_gap_days"]:
        criteria_met["stable_income_pay_gap_days"] = int(median_pay_gap)

    # Matches if cash_buffer < 2 AND (growth < 1% OR inflow < $100) AND pay_gap ≤ 45
    has_low_cash_buffer = cash_buffer < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_cash_buffer_months"]
    has_poor_savings = (
        growth_rate < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_growth_rate_pct"]
        or net_inflow < PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_net_inflow"]
    )
    has_stable_income = (
        median_pay_gap > 0 and
        median_pay_gap <= PERSONA_THRESHOLDS["Cash Flow Optimizer"]["max_pay_gap_days"]
    )

    matches = has_low_cash_buffer and has_poor_savings and has_stable_income

    return matches, criteria_met


def assign_persona(signals: pd.Series) -> Tuple[str, Dict]:
    """
    Assign a persona to a user based on priority-ordered criteria.

    Priority order:
    1. High Utilization (immediate credit strain)
    2. Variable Income Budgeter (income stability)
    3. Subscription-Heavy (spending optimization)
    4. Cash Flow Optimizer (cash flow management)
    5. Savings Builder (positive reinforcement)
    6. General (default for users with minimal signals)

    Args:
        signals: Row from signals DataFrame for a single user

    Returns:
        (persona_name, all_criteria_checks_dict)
    """
    # Run all persona checks
    checks = {
        "High Utilization": check_high_utilization(signals),
        "Variable Income Budgeter": check_variable_income(signals),
        "Subscription-Heavy": check_subscription_heavy(signals),
        "Cash Flow Optimizer": check_cash_flow_optimizer(signals),
        "Savings Builder": check_savings_builder(signals),
    }

    # Apply priority-based assignment
    for persona_name in PERSONA_PRIORITY:
        if persona_name == "General":
            # Skip 'General' - it's the default fallback
            continue

        if persona_name in checks:
            matches, criteria = checks[persona_name]
            if matches:
                # Return first matching persona based on priority
                all_checks = {p: c for p, (m, c) in checks.items()}
                return persona_name, {
                    "assigned_persona": persona_name,
                    "criteria_met": criteria,
                    "all_checks": all_checks,
                }

    # Default to 'General' if no persona matches
    all_checks = {p: c for p, (m, c) in checks.items()}
    return "General", {"assigned_persona": "General", "criteria_met": {}, "all_checks": all_checks}


def assign_all_personas(
    signals_path: str = "features/signals.parquet",
    db_path: str = "data/users.sqlite",
    traces_dir: str = "docs/traces",
) -> pd.DataFrame:
    """
    Assign personas to all users and persist to database and trace files.

    Args:
        signals_path: Path to signals parquet file
        db_path: Path to SQLite database
        traces_dir: Directory for trace JSON files

    Returns:
        DataFrame with user_id, persona, criteria_met columns
    """
    print(f"Loading signals from {signals_path}...")
    signals_df = pd.read_parquet(signals_path)
    print(f"Loaded {len(signals_df)} users with signals.")

    # Assign personas
    assignments = []
    for idx, row in signals_df.iterrows():
        user_id = row["user_id"]
        persona, persona_data = assign_persona(row)

        assignments.append(
            {
                "assignment_id": str(uuid.uuid4()),
                "user_id": user_id,
                "persona": persona,
                "criteria_met": json.dumps(persona_data["criteria_met"]),
                "assigned_at": datetime.now().isoformat(),
            }
        )

        # Update trace JSON
        update_trace_file(user_id, persona_data, traces_dir)

    assignments_df = pd.DataFrame(assignments)

    # Persist to SQLite
    print(f"\nWriting {len(assignments_df)} persona assignments to {db_path}...")
    conn = sqlite3.connect(db_path)

    # Clear existing assignments (for re-runs)
    conn.execute("DELETE FROM persona_assignments")

    # Insert new assignments
    assignments_df.to_sql("persona_assignments", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    # Print summary statistics
    print("\n" + "=" * 60)
    print("PERSONA ASSIGNMENT SUMMARY")
    print("=" * 60)
    persona_counts = assignments_df["persona"].value_counts()
    for persona, count in persona_counts.items():
        pct = (count / len(assignments_df)) * 100
        print(f"{persona:25s} {count:3d} users ({pct:5.1f}%)")
    print("=" * 60)
    print(f"Total users assigned:     {len(assignments_df)}")
    print("Coverage:                 100.0%")
    print("=" * 60)

    return assignments_df


def update_trace_file(user_id: str, persona_data: Dict, traces_dir: str):
    """
    Update or create trace JSON file with persona assignment data.

    Args:
        user_id: User identifier
        persona_data: Persona assignment data dictionary
        traces_dir: Directory for trace files
    """
    traces_path = Path(traces_dir)
    traces_path.mkdir(exist_ok=True)

    trace_file = traces_path / f"{user_id}.json"

    # Load existing trace or create new
    if trace_file.exists():
        with open(trace_file, "r") as f:
            trace = json.load(f)
    else:
        trace = {"user_id": user_id, "created_at": datetime.now().isoformat()}

    # Add persona assignment section
    trace["persona_assignment"] = {
        "persona": persona_data["assigned_persona"],
        "criteria_met": persona_data["criteria_met"],
        "all_checks": persona_data["all_checks"],
        "timestamp": datetime.now().isoformat(),
    }

    # Write updated trace
    with open(trace_file, "w") as f:
        json.dump(trace, f, indent=2)


if __name__ == "__main__":
    # CLI entry point
    print("=" * 60)
    print("SpendSense PR #3: Persona Assignment System")
    print("=" * 60)
    print()

    assignments = assign_all_personas()

    print("\nPersona assignment complete!")
    print("Results stored in: data/users.sqlite (persona_assignments table)")
    print("Trace files updated in: docs/traces/")
