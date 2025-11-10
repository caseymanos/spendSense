"""
FastAPI request/response models for SpendSense MVP V2.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Request models
class ConsentRequest(BaseModel):
    """Request to grant or revoke consent"""

    user_id: str
    consent_granted: bool


class FeedbackRequest(BaseModel):
    """User feedback on recommendations"""

    user_id: str
    recommendation_id: str
    feedback_type: str = Field(..., description="helpful, not_helpful, inappropriate")
    comment: Optional[str] = None


class OperatorReviewRequest(BaseModel):
    """Operator review action"""

    recommendation_id: str
    action: str = Field(..., description="approve, override, flag")
    reason: Optional[str] = None
    override_content: Optional[str] = None


# Response models
class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str = "0.1.0"


class UserProfileResponse(BaseModel):
    """User profile with persona and signals"""

    user_id: str
    name: str
    consent_granted: bool
    persona: Optional[str] = None
    signals: Optional[dict] = None


class RecommendationResponse(BaseModel):
    """Recommendation item"""

    recommendation_id: str
    type: str  # education or partner_offer
    title: str
    rationale: str
    disclaimer: str
    content: Optional[dict] = None
    topic: Optional[str] = None
    source: Optional[str] = None  # auto_generated, operator_created, operator_override
    created_by: Optional[str] = None  # operator name if applicable


class UserRecommendationsResponse(BaseModel):
    """All recommendations for a user"""

    user_id: str
    persona: Optional[str] = None
    recommendations: List[RecommendationResponse]
    generated_at: datetime


class UserSummary(BaseModel):
    """Lightweight user object for listings and consent updates"""

    user_id: str
    name: str
    consent_granted: bool


class ConsentUpdateResponse(BaseModel):
    """Response for consent grant/revoke"""

    success: bool
    user: UserSummary


class EvaluationSummaryResponse(BaseModel):
    """System evaluation metrics"""

    coverage: float
    explainability: float
    latency: float
    fairness: dict
    auditability: float
    timestamp: datetime


class VideoResponse(BaseModel):
    """Educational video linked to a recommendation topic"""

    video_id: str
    youtube_id: str
    title: str
    channel_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: str
    description: Optional[str] = None


# Operator Recommendation Models
class CreateOperatorRecommendationRequest(BaseModel):
    """Request to create operator recommendation"""

    user_id: str
    type: str  # education or partner_offer
    title: str
    description: str
    category: str
    topic: str
    rationale: str
    disclaimer: Optional[str] = None
    content: Optional[dict] = None
    operator_name: str


class UpdateOperatorRecommendationRequest(BaseModel):
    """Request to update operator recommendation"""

    title: str
    description: str
    category: str
    topic: str
    rationale: str
    disclaimer: Optional[str] = None
    content: Optional[dict] = None
    operator_name: str


class OverrideRecommendationRequest(BaseModel):
    """Request to override auto-generated recommendation"""

    user_id: str
    type: str
    title: str
    description: str
    category: str
    topic: str
    rationale: str
    disclaimer: Optional[str] = None
    content: Optional[dict] = None
    operator_name: str


class BulkEditRequest(BaseModel):
    """Request for bulk editing recommendations"""

    recommendation_ids: List[str]
    updates: dict  # Fields to update
    operator_name: str
