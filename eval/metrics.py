"""
Evaluation Metrics Module

This module calculates the 6 core metrics for evaluating the SpendSense system:
1. Coverage: % of users with meaningful persona + ≥3 behaviors
2. Explainability: % of recommendations with rationales
3. Relevance: Rule-based persona→content category alignment
4. Latency: Mean time to generate recommendations per user
5. Auditability: % of users with complete trace JSONs

Note: Fairness metric is in separate fairness.py module due to complexity.

All metrics return (value, metadata_dict) tuples for detailed reporting.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List

import pandas as pd
import numpy as np

# Import recommendation engine for latency testing
from recommend.engine import generate_recommendations


# ============================================
# PERSONA → CONTENT CATEGORY MAPPINGS
# ============================================

PERSONA_CATEGORY_MAP = {
    "high_utilization": [
        "credit_basics",
        "debt_paydown",
        "payment_automation",
        "counseling",
        "credit_card",  # partner offers
        "budgeting_app",
    ],
    "variable_income": [
        "budgeting",
        "emergency_fund",
        "tax_planning",
        "budgeting_app",  # partner offers
        "savings_account",
        "tax_app",
    ],
    "subscription_heavy": [
        "subscription_management",
        "subscription_app",  # partner offers
        "phone_service",
    ],
    "savings_builder": [
        "goal_setting",
        "savings_optimization",
        "savings_automation",
        "savings_account",  # partner offers
        "investment_account",
        "cd_account",
    ],
}


# ============================================
# DATA LOADING HELPERS
# ============================================


def load_users_from_db(db_path: str = "data/users.sqlite") -> pd.DataFrame:
    """
    Load all users from SQLite database.

    Args:
        db_path: Path to SQLite database

    Returns:
        DataFrame with user records (user_id, name, consent_granted, demographics)
    """
    conn = sqlite3.connect(db_path)
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return users_df


def load_personas_from_db(db_path: str = "data/users.sqlite") -> pd.DataFrame:
    """
    Load persona assignments from SQLite database.

    Args:
        db_path: Path to SQLite database

    Returns:
        DataFrame with persona assignments (assignment_id, user_id, persona, criteria_met)
    """
    conn = sqlite3.connect(db_path)
    personas_df = pd.read_sql_query("SELECT * FROM persona_assignments", conn)
    conn.close()
    return personas_df


def load_signals_from_parquet(
    parquet_path: str = "features/signals.parquet",
) -> pd.DataFrame:
    """
    Load behavioral signals from Parquet file.

    Args:
        parquet_path: Path to signals Parquet file

    Returns:
        DataFrame with all behavioral signals (30d and 180d windows)
    """
    signals_df = pd.read_parquet(parquet_path)
    return signals_df


def load_trace_jsons(traces_dir: str = "docs/traces") -> List[Dict[str, Any]]:
    """
    Load all trace JSON files from directory.

    Args:
        traces_dir: Directory containing user trace JSONs

    Returns:
        List of trace dictionaries
    """
    traces_path = Path(traces_dir)
    trace_files = sorted(traces_path.glob("user_*.json"))

    traces = []
    for trace_file in trace_files:
        with open(trace_file, "r") as f:
            trace = json.load(f)
            traces.append(trace)

    return traces


# ============================================
# METRIC 1: COVERAGE
# ============================================


def calculate_coverage(
    users_df: pd.DataFrame,
    personas_df: pd.DataFrame,
    signals_df: pd.DataFrame,
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate coverage metric: % of users with meaningful persona + ≥3 behaviors.

    Coverage excludes 'general' persona (per user decision) since 'general' is assigned
    when no persona criteria are met.

    A behavior is detected if any signal in that category is non-zero:
    - Subscriptions: recurring_count > 0
    - Savings: net_inflow > 0 OR growth_rate > 0
    - Credit: utilization > 0 OR has_interest
    - Income: num_paychecks > 0

    Args:
        users_df: User records from SQLite
        personas_df: Persona assignments from SQLite
        signals_df: Behavioral signals from Parquet

    Returns:
        Tuple of (coverage_pct, metadata_dict)
    """
    total_users = len(users_df)

    # Count users with meaningful persona (exclude 'general')
    users_with_persona = personas_df[personas_df["persona"] != "general"].copy()
    num_users_with_persona = len(users_with_persona)

    # Count behaviors per user (using 180d window for broader coverage)
    behavior_counts = signals_df.apply(
        lambda row: sum(
            [
                row["sub_180d_recurring_count"] > 0,  # Subscriptions
                row["sav_180d_net_inflow"] > 0
                or row["sav_180d_growth_rate_pct"] > 0,  # Savings
                row["credit_max_util_pct"] > 0
                or row["credit_has_interest"],  # Credit
                row["inc_180d_num_paychecks"] > 0,  # Income
            ]
        ),
        axis=1,
    )

    # Users with ≥3 behaviors
    users_with_3_behaviors = (behavior_counts >= 3).sum()

    # Coverage = users with BOTH meaningful persona AND ≥3 behaviors
    # (Merge to find intersection)
    merged = users_with_persona.merge(signals_df, on="user_id")
    merged_behavior_counts = merged.apply(
        lambda row: sum(
            [
                row["sub_180d_recurring_count"] > 0,
                row["sav_180d_net_inflow"] > 0
                or row["sav_180d_growth_rate_pct"] > 0,
                row["credit_max_util_pct"] > 0 or row["credit_has_interest"],
                row["inc_180d_num_paychecks"] > 0,
            ]
        ),
        axis=1,
    )
    users_with_both = (merged_behavior_counts >= 3).sum()

    coverage_pct = (users_with_both / total_users) * 100 if total_users > 0 else 0.0

    metadata = {
        "total_users": int(total_users),
        "users_with_meaningful_persona": int(num_users_with_persona),
        "users_with_3_behaviors": int(users_with_3_behaviors),
        "users_with_both": int(users_with_both),
        "coverage_percentage": round(float(coverage_pct), 2),
        "target": 100.0,
        "passes": bool(coverage_pct >= 100.0),
    }

    return coverage_pct, metadata


# ============================================
# METRIC 2: EXPLAINABILITY
# ============================================


def calculate_explainability(traces: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate explainability metric: % of recommendations with non-empty rationale.

    A recommendation is considered explainable if it has a 'rationale' field with
    non-empty string content.

    Args:
        traces: List of trace JSON dictionaries

    Returns:
        Tuple of (explainability_pct, metadata_dict)
    """
    total_recs = 0
    recs_with_rationale = 0
    recs_without_rationale = []

    for trace in traces:
        if "recommendations" not in trace:
            continue

        recs = trace["recommendations"].get("recommendations", [])
        user_id = trace.get("user_id", "unknown")

        for rec in recs:
            total_recs += 1
            rationale = rec.get("rationale", "").strip()

            if rationale:
                recs_with_rationale += 1
            else:
                recs_without_rationale.append(
                    {
                        "user_id": user_id,
                        "title": rec.get("title", "unknown"),
                        "type": rec.get("type", "unknown"),
                    }
                )

    explainability_pct = (
        (recs_with_rationale / total_recs) * 100 if total_recs > 0 else 0.0
    )

    metadata = {
        "total_recommendations": int(total_recs),
        "recommendations_with_rationale": int(recs_with_rationale),
        "recommendations_without_rationale": int(len(recs_without_rationale)),
        "explainability_percentage": round(float(explainability_pct), 2),
        "target": 100.0,
        "passes": bool(explainability_pct >= 100.0),
        "missing_rationales_sample": recs_without_rationale[
            :5
        ],  # First 5 examples
    }

    return explainability_pct, metadata


# ============================================
# METRIC 3: RELEVANCE
# ============================================


def calculate_relevance(traces: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate relevance metric: Rule-based persona → content category alignment.

    A recommendation is relevant if its category matches the expected categories
    for the user's assigned persona (based on PERSONA_CATEGORY_MAP).

    Args:
        traces: List of trace JSON dictionaries

    Returns:
        Tuple of (relevance_pct, metadata_dict)
    """
    total_recs = 0
    relevant_recs = 0
    irrelevant_recs = []

    for trace in traces:
        if "persona_assignment" not in trace or "recommendations" not in trace:
            continue

        persona = trace["persona_assignment"].get("persona")
        if persona not in PERSONA_CATEGORY_MAP:
            continue  # Skip 'general' or unknown personas

        expected_categories = PERSONA_CATEGORY_MAP[persona]
        recs = trace["recommendations"].get("recommendations", [])
        user_id = trace.get("user_id", "unknown")

        for rec in recs:
            total_recs += 1
            category = rec.get("category", "")

            if category in expected_categories:
                relevant_recs += 1
            else:
                irrelevant_recs.append(
                    {
                        "user_id": user_id,
                        "persona": persona,
                        "title": rec.get("title", "unknown"),
                        "category": category,
                        "expected_categories": expected_categories,
                    }
                )

    relevance_pct = (relevant_recs / total_recs) * 100 if total_recs > 0 else 0.0

    metadata = {
        "total_recommendations": int(total_recs),
        "relevant_recommendations": int(relevant_recs),
        "irrelevant_recommendations": int(len(irrelevant_recs)),
        "relevance_percentage": round(float(relevance_pct), 2),
        "target": 90.0,
        "passes": bool(relevance_pct >= 90.0),
        "irrelevant_sample": irrelevant_recs[:5],  # First 5 examples
    }

    return relevance_pct, metadata


# ============================================
# METRIC 4: LATENCY
# ============================================


def calculate_latency(
    users_df: pd.DataFrame,
    sample_size: int = None,
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate latency metric: Mean time to generate recommendations per user.

    Measures actual execution time of generate_recommendations() using time.perf_counter()
    for high-precision timing.

    Args:
        users_df: User records from SQLite
        sample_size: Number of users to sample (None = all users with consent)

    Returns:
        Tuple of (mean_latency_seconds, metadata_dict)
    """
    # Only test users with consent (since no recs generated otherwise)
    consented_users = users_df[users_df["consent_granted"] == True].copy()

    if sample_size:
        consented_users = consented_users.sample(
            n=min(sample_size, len(consented_users)), random_state=42
        )

    latencies = []

    for _, user in consented_users.iterrows():
        user_id = user["user_id"]

        start = time.perf_counter()
        try:
            _ = generate_recommendations(user_id)
            end = time.perf_counter()
            latency = end - start
            latencies.append(latency)
        except Exception as e:
            # Log error but continue
            print(f"Warning: Failed to generate recommendations for {user_id}: {e}")
            continue

    if not latencies:
        return 0.0, {"error": "No successful recommendation generations"}

    mean_latency = np.mean(latencies)
    max_latency = np.max(latencies)
    min_latency = np.min(latencies)
    p50_latency = np.percentile(latencies, 50)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)

    metadata = {
        "users_tested": int(len(latencies)),
        "mean_seconds": round(float(mean_latency), 4),
        "median_seconds": round(float(p50_latency), 4),
        "p95_seconds": round(float(p95_latency), 4),
        "p99_seconds": round(float(p99_latency), 4),
        "min_seconds": round(float(min_latency), 4),
        "max_seconds": round(float(max_latency), 4),
        "target": 5.0,
        "passes": bool(mean_latency < 5.0),
    }

    return mean_latency, metadata


# ============================================
# METRIC 5: AUDITABILITY
# ============================================


def calculate_auditability(
    users_df: pd.DataFrame,
    traces_dir: str = "docs/traces",
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate auditability metric: % of users with complete trace JSONs.

    A trace is complete if:
    - Trace file exists for user_id
    - Contains 'signals' section (behavioral detection)
    - Contains 'persona_assignment' section
    - If consent granted: Contains 'recommendations' section
    - If consent not granted: No recommendations section required

    Args:
        users_df: User records from SQLite
        traces_dir: Directory containing trace JSONs

    Returns:
        Tuple of (auditability_pct, metadata_dict)
    """
    total_users = len(users_df)
    users_with_trace = 0
    complete_traces = 0
    incomplete_details = []

    traces_path = Path(traces_dir)

    for _, user in users_df.iterrows():
        user_id = user["user_id"]
        consent = user["consent_granted"]
        trace_file = traces_path / f"{user_id}.json"

        if not trace_file.exists():
            incomplete_details.append(
                {"user_id": user_id, "reason": "trace_file_missing"}
            )
            continue

        users_with_trace += 1

        # Load and validate trace
        with open(trace_file, "r") as f:
            trace = json.load(f)

        has_signals = "signals" in trace
        has_persona = "persona_assignment" in trace
        has_recs = "recommendations" in trace

        if consent:
            # Consented users should have recommendations
            if has_signals and has_persona and has_recs:
                complete_traces += 1
            else:
                incomplete_details.append(
                    {
                        "user_id": user_id,
                        "consent": True,
                        "has_signals": has_signals,
                        "has_persona": has_persona,
                        "has_recommendations": has_recs,
                    }
                )
        else:
            # Non-consented users should NOT have recommendations
            if has_signals and has_persona and not has_recs:
                complete_traces += 1
            else:
                incomplete_details.append(
                    {
                        "user_id": user_id,
                        "consent": False,
                        "has_signals": has_signals,
                        "has_persona": has_persona,
                        "unexpected_recommendations": has_recs,
                    }
                )

    auditability_pct = (users_with_trace / total_users) * 100 if total_users > 0 else 0.0
    completeness_pct = (complete_traces / total_users) * 100 if total_users > 0 else 0.0

    metadata = {
        "total_users": int(total_users),
        "users_with_trace_file": int(users_with_trace),
        "users_with_complete_trace": int(complete_traces),
        "auditability_percentage": round(float(auditability_pct), 2),
        "completeness_percentage": round(float(completeness_pct), 2),
        "target": 100.0,
        "passes": bool(completeness_pct >= 100.0),
        "incomplete_traces_sample": incomplete_details[:5],
    }

    return completeness_pct, metadata


# ============================================
# AGGREGATE METRICS FUNCTION
# ============================================


def calculate_all_metrics(
    db_path: str = "data/users.sqlite",
    signals_path: str = "features/signals.parquet",
    traces_dir: str = "docs/traces",
    latency_sample_size: int = None,
) -> Dict[str, Any]:
    """
    Calculate all 5 metrics (coverage, explainability, relevance, latency, auditability).

    Note: Fairness metric is calculated separately in fairness.py due to complexity.

    Args:
        db_path: Path to SQLite database
        signals_path: Path to signals Parquet file
        traces_dir: Directory containing trace JSONs
        latency_sample_size: Number of users for latency test (None = all consented)

    Returns:
        Dictionary with all metrics and metadata
    """
    print("Loading data...")
    users_df = load_users_from_db(db_path)
    personas_df = load_personas_from_db(db_path)
    signals_df = load_signals_from_parquet(signals_path)
    traces = load_trace_jsons(traces_dir)

    print(f"Loaded {len(users_df)} users, {len(personas_df)} personas, {len(traces)} traces")

    results = {}

    # Metric 1: Coverage
    print("\nCalculating coverage...")
    coverage_pct, coverage_meta = calculate_coverage(users_df, personas_df, signals_df)
    results["coverage"] = {
        "value": coverage_pct,
        "metadata": coverage_meta,
    }

    # Metric 2: Explainability
    print("Calculating explainability...")
    explainability_pct, explainability_meta = calculate_explainability(traces)
    results["explainability"] = {
        "value": explainability_pct,
        "metadata": explainability_meta,
    }

    # Metric 3: Relevance
    print("Calculating relevance...")
    relevance_pct, relevance_meta = calculate_relevance(traces)
    results["relevance"] = {
        "value": relevance_pct,
        "metadata": relevance_meta,
    }

    # Metric 4: Latency
    print("Calculating latency...")
    mean_latency, latency_meta = calculate_latency(users_df, latency_sample_size)
    results["latency"] = {
        "value": mean_latency,
        "metadata": latency_meta,
    }

    # Metric 5: Auditability
    print("Calculating auditability...")
    auditability_pct, auditability_meta = calculate_auditability(users_df, traces_dir)
    results["auditability"] = {
        "value": auditability_pct,
        "metadata": auditability_meta,
    }

    # Summary
    results["summary"] = {
        "total_users": len(users_df),
        "total_personas": len(personas_df),
        "total_traces": len(traces),
        "metrics_calculated": 5,
        "all_metrics_pass": all(
            results[metric]["metadata"].get("passes", False)
            for metric in ["coverage", "explainability", "relevance", "latency", "auditability"]
        ),
    }

    return results
