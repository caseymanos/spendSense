"""
API service wrappers bridging to existing data/loading utilities.

These functions adapt the shapes returned by data loaders and the
recommendation engine to the API response models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from api.models import (
    UserSummary,
    UserProfileResponse,
    RecommendationResponse,
    UserRecommendationsResponse,
)

# Reuse robust loaders defined for Reflex UI
from ui_reflex.user_app.utils.data_loaders import (
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
    """Adapt the engine output to API model."""
    payload = _engine_get_recommendations(user_id)
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
                content=None,
            )
        )

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

