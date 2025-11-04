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
    type: str  # education or offer
    title: str
    rationale: str
    disclaimer: str
    content: Optional[dict] = None


class UserRecommendationsResponse(BaseModel):
    """All recommendations for a user"""

    user_id: str
    persona: Optional[str] = None
    recommendations: List[RecommendationResponse]
    generated_at: datetime


class EvaluationSummaryResponse(BaseModel):
    """System evaluation metrics"""

    coverage: float
    explainability: float
    latency: float
    fairness: dict
    auditability: float
    timestamp: datetime
