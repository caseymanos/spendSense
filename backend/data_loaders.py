"""
Data loading utilities for FastAPI backend.

Provides clean interface for accessing user data, personas, and recommendations.
All business logic, guardrails, and trace logging remain in the original modules.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import sqlite3
import json

from recommend.engine import generate_recommendations
from guardrails.consent import (
    grant_consent as _grant_consent,
    revoke_consent as _revoke_consent,
)

# =============================================================================
# PATHS
# =============================================================================

# Get project root (go up from backend to project root)
PROJECT_ROOT = Path(__file__).parent.parent

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
