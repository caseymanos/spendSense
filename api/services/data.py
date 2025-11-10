"""
API service wrappers bridging to existing data/loading utilities.

These functions adapt the shapes returned by data loaders and the
recommendation engine to the API response models.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from api.models import (
    UserSummary,
    UserProfileResponse,
    RecommendationResponse,
    UserRecommendationsResponse,
)

# Use backend data loaders
from backend.data_loaders import (
    load_all_users,
    load_user_data,
    load_persona_assignment,
    load_behavioral_signals,
    get_recommendations as _engine_get_recommendations,
    grant_user_consent,
    revoke_user_consent,
)


def list_users() -> List[UserSummary]:
    """Return all users with consent status for selection lists."""
    users = load_all_users() or []
    return [
        UserSummary(
            user_id=u.get("user_id", ""),
            name=u.get("name", "Unknown"),
            consent_granted=bool(u.get("consent_granted", False)),
        )
        for u in users
    ]


def get_profile(user_id: str) -> Optional[UserProfileResponse]:
    """Compose profile from user row, persona assignment, and signals."""
    user = load_user_data(user_id)
    if not user:
        return None

    persona = load_persona_assignment(user_id)
    signals = load_behavioral_signals(user_id)

    return UserProfileResponse(
        user_id=user.get("user_id", user_id),
        name=user.get("name", "Unknown"),
        consent_granted=bool(user.get("consent_granted", False)),
        persona=(persona or {}).get("persona"),
        signals=signals or {},
    )


def _slugify(text: str) -> str:
    """Basic slug for stable recommendation ids."""
    import re

    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:64] if text else "item"


def get_recommendations(user_id: str) -> UserRecommendationsResponse:
    """Fetch pre-generated recommendations from database."""
    import json
    import sqlite3
    from pathlib import Path

    # Connect to database
    db_path = Path(__file__).parent.parent.parent / "data" / "users.sqlite"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Fetch pre-generated recommendations
    cursor.execute(
        "SELECT recommendations_json, generated_at FROM recommendations WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()

    # If no pre-generated recommendations found, fall back to on-the-fly generation
    if not result:
        payload = _engine_get_recommendations(user_id)
    else:
        recommendations_json, generated_at_str = result
        payload = json.loads(recommendations_json)

    recs = payload.get("recommendations", [])

    items: List[RecommendationResponse] = []
    for idx, rec in enumerate(recs):
        rid = f"{idx}-{rec.get('type','item')}-{_slugify(rec.get('title',''))}"
        items.append(
            RecommendationResponse(
                recommendation_id=rid,
                type=rec.get("type", "education"),
                title=rec.get("title", "Untitled"),
                rationale=rec.get("rationale", ""),
                disclaimer=rec.get("disclaimer", ""),
                content=rec.get("content"),
                topic=rec.get("topic"),
            )
        )

    # Parse timestamp
    if result:
        try:
            generated_at = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00"))
        except Exception:
            generated_at = datetime.now()
    else:
        ts = payload.get("metadata", {}).get("timestamp")
        try:
            generated_at = (
                datetime.fromisoformat(ts.replace("Z", "+00:00")) if isinstance(ts, str) else datetime.now()
            )
        except Exception:
            generated_at = datetime.now()

    return UserRecommendationsResponse(
        user_id=user_id,
        persona=payload.get("persona"),
        recommendations=items,
        generated_at=generated_at,
    )


def get_persona_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get persona-specific transactions for a user."""
    from backend.data_loaders import load_persona_transactions

    transactions = load_persona_transactions(user_id, limit=limit)
    return transactions if transactions else []


def set_consent(user_id: str, granted: bool) -> Optional[UserSummary]:
    """Grant or revoke consent, returning updated user summary."""
    ok = grant_user_consent(user_id) if granted else revoke_user_consent(user_id)
    if not ok:
        return None
    user = load_user_data(user_id) or {"user_id": user_id, "name": "Unknown", "consent_granted": granted}
    return UserSummary(
        user_id=user.get("user_id", user_id),
        name=user.get("name", "Unknown"),
        consent_granted=bool(user.get("consent_granted", False)),
    )


def list_profiles_batch() -> List[UserProfileResponse]:
    """Return all user profiles with personas in a single batch call."""
    users = load_all_users() or []
    profiles = []

    for u in users:
        user_id = u.get("user_id", "")
        persona = load_persona_assignment(user_id)
        signals = load_behavioral_signals(user_id)

        profiles.append(
            UserProfileResponse(
                user_id=user_id,
                name=u.get("name", "Unknown"),
                consent_granted=bool(u.get("consent_granted", False)),
                persona=(persona or {}).get("persona"),
                signals=signals or {},
            )
        )

    return profiles


def get_recommendations_summary() -> Dict[str, Any]:
    """Get aggregate recommendation counts for all users."""
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent.parent.parent / "data" / "users.sqlite"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Count total recommendations across all users
    cursor.execute("""
        SELECT
            COUNT(*) as total_users,
            SUM(json_array_length(recommendations_json, '$.recommendations')) as total_recommendations
        FROM recommendations
    """)
    result = cursor.fetchone()

    # Count users with consent
    cursor.execute("SELECT COUNT(*) FROM users WHERE consent_granted = 1")
    users_with_consent = cursor.fetchone()[0]

    conn.close()

    return {
        "total_users": result[0] if result else 0,
        "total_recommendations": result[1] if result and result[1] else 0,
        "users_with_consent": users_with_consent,
        "tone_violations": [],  # Placeholder - would need guardrail log analysis
        "blocked_offers": [],   # Placeholder - would need guardrail log analysis
    }

