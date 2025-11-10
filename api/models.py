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


class CreditCardInfo(BaseModel):
    """Credit card financial details"""

    account_id: str
    mask: str
    balance: float
    credit_limit: float
    available_credit: float
    utilization: float
    apr: Optional[float] = None
    monthly_interest: Optional[float] = None
    minimum_payment: Optional[float] = None


class UserProfileResponse(BaseModel):
    """User profile with persona and signals"""

    user_id: str
    name: str
    consent_granted: bool
    persona: Optional[str] = None
    signals: Optional[dict] = None
    credit_cards: Optional[List["CreditCardInfo"]] = None


class RecommendationResponse(BaseModel):
    """Recommendation item"""

    recommendation_id: str
    type: str  # education or partner_offer
    title: str
    rationale: str
    disclaimer: str
    content: Optional[dict] = None
    topic: Optional[str] = None


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


class BehavioralSignalsResponse(BaseModel):
    """Behavioral signals for a user"""

    user_id: str

    # Subscription signals
    sub_30d_recurring_count: Optional[int] = None
    sub_30d_monthly_spend: Optional[float] = None
    sub_30d_share_pct: Optional[float] = None
    sub_180d_recurring_count: Optional[int] = None
    sub_180d_monthly_spend: Optional[float] = None
    sub_180d_share_pct: Optional[float] = None

    # Savings signals
    sav_30d_net_inflow: Optional[float] = None
    sav_30d_growth_rate_pct: Optional[float] = None
    sav_30d_emergency_fund_months: Optional[float] = None
    sav_30d_balance: Optional[float] = None
    sav_180d_net_inflow: Optional[float] = None
    sav_180d_growth_rate_pct: Optional[float] = None
    sav_180d_emergency_fund_months: Optional[float] = None
    sav_180d_balance: Optional[float] = None

    # Credit signals
    credit_max_util_pct: Optional[float] = None
    credit_avg_util_pct: Optional[float] = None
    credit_flag_30: Optional[bool] = None
    credit_flag_50: Optional[bool] = None
    credit_flag_80: Optional[bool] = None
    credit_min_payment_only: Optional[bool] = None
    credit_has_interest: Optional[bool] = None
    credit_interest_charges: Optional[bool] = None
    credit_is_overdue: Optional[bool] = None
    credit_num_cards: Optional[int] = None

    # Income signals
    inc_30d_median_pay_gap_days: Optional[int] = None
    inc_30d_variability: Optional[float] = None
    inc_30d_cash_buffer_months: Optional[float] = None
    inc_30d_num_paychecks: Optional[int] = None
    inc_30d_avg_paycheck: Optional[float] = None
    inc_180d_median_pay_gap_days: Optional[int] = None
    inc_180d_variability: Optional[float] = None
    inc_180d_cash_buffer_months: Optional[float] = None
    inc_180d_num_paychecks: Optional[int] = None
    inc_180d_avg_paycheck: Optional[float] = None
