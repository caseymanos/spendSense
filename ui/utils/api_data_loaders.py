"""
API-based data loading utilities for NiceGUI operator dashboard.

Fetches data from the FastAPI backend instead of local files.
Works in production (Railway) where local files are ephemeral.
"""

import os
import json
import pandas as pd
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# API URL configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


def load_all_users() -> pd.DataFrame:
    """
    Load all users from API /profiles/batch endpoint (optimized batch call).

    Returns:
        DataFrame with columns: user_id, name, consent_granted, persona, etc.
    """
    try:
        # Use batch endpoint to get all profiles in one call (instead of 100+ calls)
        response = requests.get(f"{API_URL}/profiles/batch", timeout=30)
        response.raise_for_status()
        profiles_data = response.json()

        if not profiles_data:
            return pd.DataFrame()

        # Convert to DataFrame
        users_df = pd.DataFrame(profiles_data)

        # Ensure consent_granted is boolean
        if "consent_granted" in users_df.columns:
            users_df["consent_granted"] = users_df["consent_granted"].astype(bool)

        # Add placeholder columns that operator dashboard expects (if not present)
        if "age" not in users_df.columns:
            users_df["age"] = None
        if "gender" not in users_df.columns:
            users_df["gender"] = None
        if "income_tier" not in users_df.columns:
            users_df["income_tier"] = None
        if "region" not in users_df.columns:
            users_df["region"] = None
        if "persona_assigned_at" not in users_df.columns:
            users_df["persona_assigned_at"] = None
        if "consent_timestamp" not in users_df.columns:
            users_df["consent_timestamp"] = None
        if "revoked_timestamp" not in users_df.columns:
            users_df["revoked_timestamp"] = None

        return users_df
    except Exception as e:
        print(f"Error loading users from API: {e}")
        return pd.DataFrame()


def load_all_signals() -> pd.DataFrame:
    """
    Load behavioral signals from API.

    Note: This is not yet implemented in the API, so returns empty DataFrame.
    """
    # TODO: Add /signals endpoint to API
    return pd.DataFrame()


def load_transactions() -> pd.DataFrame:
    """
    Load transactions from API.

    Note: This is not yet implemented in the API, so returns empty DataFrame.
    """
    # TODO: Add /transactions endpoint to API
    return pd.DataFrame()


def load_user_trace(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Load decision trace for a specific user from recommendations endpoint.

    Args:
        user_id: User ID to load trace for

    Returns:
        Dictionary containing trace data in expected format, or None if not found
    """
    try:
        response = requests.get(f"{API_URL}/recommendations/{user_id}", timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        api_response = response.json()

        # Transform API response to match trace file format expected by operator dashboard
        # API format: {user_id, persona, recommendations: [...], generated_at}
        # Expected format: {recommendations: {recommendations: [...], persona, consent_granted, timestamp}}
        trace = {
            "user_id": api_response.get("user_id"),
            "recommendations": {
                "recommendations": api_response.get("recommendations", []),
                "persona": api_response.get("persona"),
                "consent_granted": api_response.get("consent_granted"),  # May be None
                "timestamp": api_response.get("generated_at", datetime.now().isoformat()),
                "source": "rule_based"  # Default to rule-based
            }
        }

        return trace
    except Exception as e:
        print(f"Error loading trace for {user_id} from API: {e}")
        return None


def load_persona_distribution() -> Dict[str, int]:
    """
    Calculate persona distribution from users endpoint.

    Returns:
        Dictionary mapping persona names to counts
    """
    try:
        users_df = load_all_users()
        if users_df.empty or "persona" not in users_df.columns:
            return {}

        # Count personas
        persona_counts = users_df["persona"].value_counts()
        return dict(persona_counts)
    except Exception as e:
        print(f"Error calculating persona distribution: {e}")
        return {}


def load_guardrail_summary() -> Dict[str, Any]:
    """
    Aggregate guardrail decisions from recommendation summary endpoint (optimized batch call).

    Returns:
        Dictionary with summary metrics:
        - total_users: Total users
        - users_with_consent: Users who granted consent
        - tone_violations: List of all tone violations
        - blocked_offers: List of all blocked offers
        - total_recommendations: Total recommendations generated
    """
    try:
        # Use batch endpoint to get summary in one call (instead of 100+ calls)
        response = requests.get(f"{API_URL}/recommendations/summary/all", timeout=30)
        response.raise_for_status()
        summary = response.json()
        return summary
    except Exception as e:
        print(f"Error loading guardrail summary: {e}")
        return {
            "total_users": 0,
            "users_with_consent": 0,
            "tone_violations": [],
            "blocked_offers": [],
            "total_recommendations": 0,
        }


def load_config() -> Dict[str, Any]:
    """
    Load configuration (placeholder - not stored in API yet).

    Returns:
        Dictionary with default configuration values
    """
    return {
        "seed": 42,
        "num_users": 100,
        "months_history": 6,
        "avg_transactions_per_month": 30,
        "generation_timestamp": datetime.now().isoformat(),
    }


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration (placeholder - not implemented in API).

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    print("Warning: save_config is not implemented for API-based loaders")
    return False


def log_operator_override(
    user_id: str,
    operator_name: str,
    action: str,
    reason: str,
    recommendation_title: str = None,
) -> tuple[bool, str]:
    """
    Log operator override (placeholder - not implemented in API).

    Args:
        user_id: User ID
        operator_name: Name of operator performing action
        action: Action type ("approve", "override", "flag")
        reason: Reason for action
        recommendation_title: Optional recommendation title

    Returns:
        Tuple of (success: bool, message: str)
    """
    # TODO: Add operator logging endpoint to API
    print(f"Warning: Operator override logging not yet implemented in API")
    print(f"  User: {user_id}, Action: {action}, Reason: {reason}")
    return True, "Logged locally (API logging not yet implemented)"


# Paths for backward compatibility (not used in API mode)
DB_PATH = None
SIGNALS_PATH = None
TRANSACTIONS_PATH = None
TRACES_DIR = None
DECISION_LOG_PATH = None
CONFIG_PATH = None
