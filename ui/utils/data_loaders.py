"""
Data loading utilities for NiceGUI operator dashboard.

Provides functions to load user data, behavioral signals, traces, and logging.
Adapted from Streamlit operator dashboard but without Streamlit dependencies.
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Resolve project root relative to this file so paths are stable regardless of CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data paths (rooted at repository root)
DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"
SIGNALS_PATH = PROJECT_ROOT / "features" / "signals.parquet"
TRANSACTIONS_PATH = PROJECT_ROOT / "data" / "transactions.parquet"
TRACES_DIR = PROJECT_ROOT / "docs" / "traces"
DECISION_LOG_PATH = PROJECT_ROOT / "docs" / "decision_log.md"
CONFIG_PATH = PROJECT_ROOT / "data" / "config.json"


def load_all_users() -> pd.DataFrame:
    """
    Load all users with consent, persona, and demographic information.

    Returns:
        DataFrame with columns: user_id, name, consent_granted, consent_timestamp,
        revoked_timestamp, age, gender, income_tier, region, persona, persona_assigned_at
    """
    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Join users with their most recent persona assignment
            query = """
            SELECT
                u.user_id,
                u.name,
                u.consent_granted,
                u.consent_timestamp,
                u.revoked_timestamp,
                u.age,
                u.gender,
                u.income_tier,
                u.region,
                p.persona,
                p.assigned_at as persona_assigned_at
            FROM users u
            LEFT JOIN persona_assignments p ON u.user_id = p.user_id
            WHERE p.assignment_id IN (
                SELECT MAX(assignment_id)
                FROM persona_assignments
                GROUP BY user_id
            ) OR p.assignment_id IS NULL
            ORDER BY u.user_id
            """
            users_df = pd.read_sql(query, conn)
            users_df["consent_granted"] = users_df["consent_granted"].astype(bool)

        return users_df
    except Exception as e:
        print(f"Error loading users: {e}")
        return pd.DataFrame()


def load_all_signals() -> pd.DataFrame:
    """
    Load all behavioral signals from parquet file.

    Returns:
        DataFrame with behavioral signal columns for all users.
    """
    if not SIGNALS_PATH.exists():
        return pd.DataFrame()

    try:
        signals_df = pd.read_parquet(SIGNALS_PATH)
        return signals_df
    except Exception as e:
        print(f"Error loading signals: {e}")
        return pd.DataFrame()


def load_transactions() -> pd.DataFrame:
    """
    Load all transactions from parquet file.

    Returns:
        DataFrame with transaction data.
    """
    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()

    try:
        transactions_df = pd.read_parquet(TRANSACTIONS_PATH)
        return transactions_df
    except Exception as e:
        print(f"Error loading transactions: {e}")
        return pd.DataFrame()


def load_user_trace(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Load decision trace JSON for a specific user.

    Args:
        user_id: User ID to load trace for

    Returns:
        Dictionary containing trace data, or None if not found
    """
    trace_file = TRACES_DIR / f"{user_id}.json"

    if not trace_file.exists():
        return None

    try:
        with open(trace_file, "r") as f:
            trace_data = json.load(f)
        return trace_data
    except Exception as e:
        print(f"Error loading trace for {user_id}: {e}")
        return None


def load_persona_distribution() -> Dict[str, int]:
    """
    Calculate persona distribution across all users.

    Returns:
        Dictionary mapping persona names to counts
    """
    if not DB_PATH.exists():
        return {}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
            SELECT persona, COUNT(*) as count
            FROM persona_assignments
            WHERE assignment_id IN (
                SELECT MAX(assignment_id)
                FROM persona_assignments
                GROUP BY user_id
            )
            GROUP BY persona
            ORDER BY count DESC
            """
            df = pd.read_sql(query, conn)

        return dict(zip(df["persona"], df["count"]))
    except Exception as e:
        print(f"Error loading persona distribution: {e}")
        return {}


def load_guardrail_summary() -> Dict[str, Any]:
    """
    Aggregate guardrail decisions across all users.

    Returns:
        Dictionary with summary metrics:
        - total_users: Total trace files found
        - users_with_consent: Users who granted consent
        - tone_violations: List of all tone violations
        - blocked_offers: List of all blocked offers
        - total_recommendations: Total recommendations generated
    """
    summary = {
        "total_users": 0,
        "users_with_consent": 0,
        "tone_violations": [],
        "blocked_offers": [],
        "total_recommendations": 0,
    }

    if not TRACES_DIR.exists():
        return summary

    trace_files = list(TRACES_DIR.glob("*.json"))
    summary["total_users"] = len([f for f in trace_files if not f.name.startswith("user_missing")])

    for trace_file in trace_files:
        try:
            with open(trace_file, "r") as f:
                trace = json.load(f)

            # Count consent
            if trace.get("recommendations", {}).get("consent_granted"):
                summary["users_with_consent"] += 1

            # Count recommendations
            recs = trace.get("recommendations", {}).get("recommendations", [])
            summary["total_recommendations"] += len(recs)

            # Extract guardrail decisions
            guardrail_decisions = trace.get("guardrail_decisions", [])
            for decision in guardrail_decisions:
                if decision.get("decision_type") == "tone_violations":
                    violations = decision.get("details", {}).get("violations", [])
                    summary["tone_violations"].extend(violations)
                elif decision.get("decision_type") == "offers_blocked":
                    blocked = decision.get("details", {}).get("blocked_offers", [])
                    summary["blocked_offers"].extend(blocked)

        except Exception:
            continue

    return summary


def load_config() -> Dict[str, Any]:
    """
    Load configuration from data/config.json.

    Returns:
        Dictionary with configuration values
    """
    if not CONFIG_PATH.exists():
        return {
            "seed": 42,
            "num_users": 100,
            "months_history": 6,
            "avg_transactions_per_month": 30,
            "generation_timestamp": datetime.now().isoformat(),
        }

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to data/config.json.

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def log_operator_override(
    user_id: str,
    operator_name: str,
    action: str,  # "approve", "override", "flag"
    reason: str,
    recommendation_title: str = None,
) -> tuple[bool, str]:
    """
    Log operator override to decision_log.md and update trace JSON.

    Args:
        user_id: User ID
        operator_name: Name of operator performing action
        action: Action type ("approve", "override", "flag")
        reason: Reason for action
        recommendation_title: Optional recommendation title

    Returns:
        Tuple of (success: bool, message: str)
    """
    timestamp = datetime.now()

    # 1. Append to decision_log.md
    try:
        log_entry = f"""
### Operator Override - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Date:** {timestamp.strftime('%Y-%m-%d')}
**Operator:** {operator_name}
**User:** {user_id}
**Action:** {action.upper()}
"""
        if recommendation_title:
            log_entry += f"**Recommendation:** {recommendation_title}  \n"

        log_entry += f"**Reason:** {reason}\n\n---\n\n"

        # Create operator overrides section if it doesn't exist
        if not DECISION_LOG_PATH.exists():
            DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DECISION_LOG_PATH, "w") as f:
                f.write("# Decision Log\n\n## Operator Overrides\n\n")

        # Check if operator overrides section exists
        with open(DECISION_LOG_PATH, "r") as f:
            content = f.read()

        if "## Operator Overrides" not in content:
            with open(DECISION_LOG_PATH, "a") as f:
                f.write("\n\n## Operator Overrides\n\n")

        # Append the override entry
        with open(DECISION_LOG_PATH, "a") as f:
            f.write(log_entry)

    except Exception as e:
        return False, f"Failed to log to decision_log.md: {e}"

    # 2. Update trace JSON
    try:
        trace_file = TRACES_DIR / f"{user_id}.json"

        if trace_file.exists():
            with open(trace_file, "r") as f:
                trace = json.load(f)
        else:
            trace = {"user_id": user_id, "guardrail_decisions": []}

        # Add operator override to guardrail_decisions
        override_entry = {
            "timestamp": timestamp.isoformat(),
            "decision_type": "operator_override",
            "operator": operator_name,
            "action": action,
            "reason": reason,
        }

        if recommendation_title:
            override_entry["recommendation_title"] = recommendation_title

        if "guardrail_decisions" not in trace:
            trace["guardrail_decisions"] = []

        trace["guardrail_decisions"].append(override_entry)

        # Write back to trace file
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        with open(trace_file, "w") as f:
            json.dump(trace, f, indent=2)

    except Exception as e:
        return False, f"Failed to update trace JSON: {e}"

    return True, "Override logged successfully"
