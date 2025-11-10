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
    """Fetch merged (auto + operator) recommendations from database."""
    import json
    import sqlite3
    from pathlib import Path
    from api.services.operator_recs import get_merged_recommendations

    # Get merged recommendations (auto + operator)
    merged_recs = get_merged_recommendations(user_id)

    items: List[RecommendationResponse] = []
    for rec in merged_recs:
        # Generate stable ID for auto-generated recs if needed
        rec_id = rec.get('recommendation_id')
        if not rec_id:
            idx = len(items)
            rec_id = f"{idx}-{rec.get('type','item')}-{_slugify(rec.get('title',''))}"

        items.append(
            RecommendationResponse(
                recommendation_id=rec_id,
                type=rec.get("type", "education"),
                title=rec.get("title", "Untitled"),
                rationale=rec.get("rationale", ""),
                disclaimer=rec.get("disclaimer", "This is educational content, not financial advice."),
                content=rec.get("content"),
                topic=rec.get("topic"),
                source=rec.get("source", "auto_generated"),
                created_by=rec.get("created_by"),
            )
        )

    # Get timestamp from recommendations table
    db_path = Path(__file__).parent.parent.parent / "data" / "users.sqlite"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT generated_at FROM recommendations WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        try:
            generated_at = datetime.fromisoformat(result[0].replace("Z", "+00:00"))
        except Exception:
            generated_at = datetime.now()
    else:
        generated_at = datetime.now()

    # Get persona
    user = load_user_data(user_id)
    persona = (load_persona_assignment(user_id) or {}).get("persona")

    return UserRecommendationsResponse(
        user_id=user_id,
        persona=persona,
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

