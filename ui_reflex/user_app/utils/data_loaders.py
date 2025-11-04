"""
Data loading utilities for Reflex UI.

Wraps existing backend modules to provide clean interface for Reflex state management.
All business logic, guardrails, and trace logging remain in the original modules.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import sqlite3
import json

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from recommend.engine import generate_recommendations
from guardrails.consent import (
    grant_consent as _grant_consent,
    revoke_consent as _revoke_consent,
    check_consent as _check_consent,
)

# =============================================================================
# PATHS
# =============================================================================

# Get project root (go up from ui_reflex/user_app/utils to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"
SIGNALS_PATH = PROJECT_ROOT / "features" / "signals.parquet"
TRANSACTIONS_PATH = PROJECT_ROOT / "data" / "transactions.parquet"
TRACES_DIR = PROJECT_ROOT / "docs" / "traces"

# =============================================================================
# USER DATA LOADING
# =============================================================================


def load_all_users() -> List[Dict[str, Any]]:
    """Load all users from database with consent status.

    Returns:
        List of user dictionaries with keys: user_id, name, consent_granted
    """
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        users_df = pd.read_sql(
            "SELECT user_id, name, consent_granted FROM users ORDER BY user_id", conn
        )

    # Convert to list of dicts for easy Reflex iteration
    return users_df.to_dict("records")


def load_user_data(user_id: str) -> Dict[str, Any]:
    """Load user demographics and consent status.

    Args:
        user_id: The user ID to load

    Returns:
        Dictionary with user data including consent status
    """
    if not DB_PATH.exists():
        return {}

    with sqlite3.connect(DB_PATH) as conn:
        user_df = pd.read_sql("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))

        if len(user_df) == 0:
            return {}

        user_data = user_df.iloc[0].to_dict()
        user_data["consent_granted"] = bool(user_data.get("consent_granted", False))

        return user_data


def load_persona_assignment(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user's persona assignment.

    Args:
        user_id: The user ID to load

    Returns:
        Dictionary with persona data or None if not assigned
    """
    if not DB_PATH.exists():
        return None

    with sqlite3.connect(DB_PATH) as conn:
        persona_df = pd.read_sql(
            "SELECT * FROM persona_assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT 1",
            conn,
            params=(user_id,),
        )

        if len(persona_df) == 0:
            return None

        persona_data = persona_df.iloc[0].to_dict()
        if "criteria_met" in persona_data and persona_data["criteria_met"]:
            try:
                persona_data["criteria_met"] = json.loads(persona_data["criteria_met"])
            except:
                persona_data["criteria_met"] = []

        return persona_data


def load_behavioral_signals(user_id: str) -> Dict[str, Any]:
    """Load user's behavioral signals from parquet file.

    Args:
        user_id: The user ID to load

    Returns:
        Dictionary with signal data (credit, subscriptions, savings, income)
    """
    if not SIGNALS_PATH.exists():
        return {}

    signals_df = pd.read_parquet(SIGNALS_PATH)
    user_signals = signals_df[signals_df["user_id"] == user_id]

    if len(user_signals) == 0:
        return {}

    signals_dict = user_signals.iloc[0].to_dict()
    signals_dict.pop("user_id", None)

    # Convert NaN values to None for cleaner display
    for key, value in signals_dict.items():
        if pd.isna(value):
            signals_dict[key] = None

    return signals_dict


def load_user_accounts(user_id: str) -> List[Dict[str, Any]]:
    """Load user's accounts from database.

    Args:
        user_id: The user ID to load

    Returns:
        List of account dictionaries
    """
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        accounts_df = pd.read_sql(
            "SELECT * FROM accounts WHERE user_id = ?", conn, params=(user_id,)
        )

    return accounts_df.to_dict("records")


def load_user_trace(user_id: str) -> Optional[Dict[str, Any]]:
    """Load decision trace JSON for a specific user.

    Args:
        user_id: The user ID to load

    Returns:
        Dictionary with trace data or None if not found
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


# =============================================================================
# RECOMMENDATIONS
# =============================================================================


def get_recommendations(user_id: str) -> Dict[str, Any]:
    """Generate recommendations for a user.

    This wraps the existing recommend.engine.generate_recommendations()
    function, which handles all business logic, guardrails, and trace logging.

    Args:
        user_id: The user ID to generate recommendations for

    Returns:
        Dictionary with recommendations and metadata
    """
    try:
        return generate_recommendations(user_id)
    except Exception as e:
        print(f"Error generating recommendations for {user_id}: {e}")
        return {
            "user_id": user_id,
            "recommendations": [],
            "metadata": {"error": str(e), "reason": "error_generating_recommendations"},
        }


# =============================================================================
# CONSENT MANAGEMENT
# =============================================================================


def grant_user_consent(user_id: str) -> bool:
    """Grant consent for a user.

    Args:
        user_id: The user ID to grant consent for

    Returns:
        True if successful, False otherwise
    """
    try:
        result = _grant_consent(user_id)
        return result.get("success", False)
    except Exception as e:
        print(f"Error granting consent for {user_id}: {e}")
        return False


def revoke_user_consent(user_id: str) -> bool:
    """Revoke consent for a user.

    Args:
        user_id: The user ID to revoke consent for

    Returns:
        True if successful, False otherwise
    """
    try:
        result = _revoke_consent(user_id)
        return result.get("success", False)
    except Exception as e:
        print(f"Error revoking consent for {user_id}: {e}")
        return False


def check_user_consent(user_id: str) -> bool:
    """Check if a user has granted consent.

    Args:
        user_id: The user ID to check

    Returns:
        True if consent granted, False otherwise
    """
    try:
        return _check_consent(user_id)
    except Exception as e:
        print(f"Error checking consent for {user_id}: {e}")
        return False


# =============================================================================
# PERSONA DESCRIPTIONS
# =============================================================================


def get_persona_description(persona: str) -> Dict[str, str]:
    """Get user-friendly description for each persona.

    Args:
        persona: The persona identifier

    Returns:
        Dictionary with title, description, icon, and color
    """
    descriptions = {
        "high_utilization": {
            "title": "Credit Optimizer",
            "description": "You're focused on optimizing credit utilization and managing card balances effectively.",
            "icon": "💳",
            "color": "#FF6B6B",
        },
        "variable_income": {
            "title": "Flexible Budgeter",
            "description": "You're managing variable income with smart budgeting strategies.",
            "icon": "📊",
            "color": "#4ECDC4",
        },
        "subscription_heavy": {
            "title": "Subscription Manager",
            "description": "You're optimizing recurring expenses and subscription spending.",
            "icon": "🔄",
            "color": "#95E1D3",
        },
        "savings_builder": {
            "title": "Savings Champion",
            "description": "You're actively building savings and growing your financial cushion.",
            "icon": "🎯",
            "color": "#38B6FF",
        },
        "general": {
            "title": "Getting Started",
            "description": "Welcome to SpendSense! Your personalized financial insights will appear as you build your transaction history.",
            "icon": "🌱",
            "color": "#A8DADC",
        },
    }

    return descriptions.get(persona, descriptions["general"])


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_database_stats() -> Dict[str, int]:
    """Get basic statistics about the database.

    Returns:
        Dictionary with stats like user_count, persona_count, etc.
    """
    stats = {
        "user_count": 0,
        "consented_count": 0,
        "has_signals": False,
        "has_traces": False,
    }

    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            stats["user_count"] = pd.read_sql("SELECT COUNT(*) as cnt FROM users", conn)[
                "cnt"
            ].iloc[0]
            stats["consented_count"] = pd.read_sql(
                "SELECT COUNT(*) as cnt FROM users WHERE consent_granted = 1", conn
            )["cnt"].iloc[0]

    stats["has_signals"] = SIGNALS_PATH.exists()
    stats["has_traces"] = TRACES_DIR.exists() and len(list(TRACES_DIR.glob("*.json"))) > 0

    return stats
