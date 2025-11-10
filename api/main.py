"""
FastAPI application for SpendSense MVP V2.
REST endpoints for user and operator interfaces.
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    HealthResponse,
    ConsentRequest,
    UserProfileResponse,
    UserRecommendationsResponse,
    FeedbackRequest,
    OperatorReviewRequest,
    EvaluationSummaryResponse,
    UserSummary,
    ConsentUpdateResponse,
    VideoResponse,
    CreateOperatorRecommendationRequest,
    UpdateOperatorRecommendationRequest,
    OverrideRecommendationRequest,
    BulkEditRequest,
)

from api.services.data import (
    list_users,
    get_profile as svc_get_profile,
    get_recommendations as svc_get_recommendations,
    set_consent as svc_set_consent,
)

from api.services.videos import (
    get_videos_by_topic,
    get_all_videos,
    get_topics_with_videos,
)


# Initialize FastAPI app
app = FastAPI(
    title="SpendSense MVP V2",
    description="Explainable, consent-aware financial behavior analysis platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=datetime.now(), version="0.1.0")


# User endpoints
@app.get("/users", response_model=list[UserSummary], tags=["Users"])
async def get_users():
    """List users for selection with consent flags."""
    return list_users()


@app.post("/consent", response_model=ConsentUpdateResponse, tags=["Users"])
async def update_consent(request: ConsentRequest):
    """Grant or revoke user consent."""
    updated = svc_set_consent(request.user_id, request.consent_granted)
    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Consent update failed")
    return {"success": True, "user": updated}


@app.get("/profile/{user_id}", response_model=UserProfileResponse, tags=["Users"])
async def get_user_profile(user_id: str):
    """Get user profile with persona and behavioral signals."""
    profile = svc_get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile


@app.get("/recommendations/{user_id}", response_model=UserRecommendationsResponse, tags=["Users"])
async def get_recommendations(user_id: str):
    """Get personalized recommendations for a user."""
    return svc_get_recommendations(user_id)


@app.get("/transactions/{user_id}", tags=["Users"])
async def get_persona_transactions(user_id: str, limit: int = 10):
    """Get persona-specific transactions for a user."""
    from api.services.data import get_persona_transactions as svc_get_persona_transactions

    transactions = svc_get_persona_transactions(user_id, limit)
    return {"user_id": user_id, "transactions": transactions, "count": len(transactions)}


@app.post("/feedback", tags=["Users"])
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on a recommendation"""
    # TODO: Implement feedback tracking in future PR
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feedback will be implemented in a future PR",
    )


# Video endpoints
@app.get("/videos/{topic}", response_model=list[VideoResponse], tags=["Videos"])
async def get_videos(topic: str):
    """Get educational videos for a specific topic."""
    videos = get_videos_by_topic(topic)
    if not videos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No videos found for topic: {topic}",
        )
    return videos


@app.get("/videos", response_model=list[VideoResponse], tags=["Videos"])
async def get_all_videos_endpoint():
    """Get all educational videos."""
    return get_all_videos()


@app.get("/videos/topics/list", response_model=list[str], tags=["Videos"])
async def get_video_topics():
    """Get list of all topics that have videos."""
    return get_topics_with_videos()


# Data generation endpoint (for Railway ephemeral storage)
@app.post("/generate-data", tags=["System"])
async def generate_data():
    """Generate synthetic user data (for ephemeral deployments)"""
    import subprocess
    try:
        subprocess.run(["python", "scripts/initialize_railway.py"], check=True)
        return {"status": "success", "message": "Full pipeline completed successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}"
        )


# Operator endpoints
@app.get("/operator/review", tags=["Operator"])
async def get_pending_reviews():
    """Get recommendations pending operator review"""
    # TODO: Implement in PR #7 (Operator Dashboard)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Operator review will be implemented in PR #7",
    )


@app.post("/operator/review", tags=["Operator"])
async def submit_review(request: OperatorReviewRequest):
    """Submit operator review decision"""
    # TODO: Implement in PR #7 (Operator Dashboard)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Operator review will be implemented in PR #7",
    )


# Operator Recommendation Management Endpoints
@app.get("/operator/recommendations/{user_id}", tags=["Operator"])
async def get_operator_recommendations(user_id: str):
    """Get all operator-managed recommendations for a user (active + overridden for audit)"""
    from api.services.operator_recs import get_operator_recs
    return get_operator_recs(user_id)


@app.post("/operator/recommendations", tags=["Operator"])
async def create_operator_recommendation(request: CreateOperatorRecommendationRequest):
    """Create new operator recommendation"""
    from api.services.operator_recs import create_operator_rec
    try:
        result = create_operator_rec(
            user_id=request.user_id,
            rec_type=request.type,
            title=request.title,
            description=request.description,
            category=request.category,
            topic=request.topic,
            rationale=request.rationale,
            operator_name=request.operator_name,
            disclaimer=request.disclaimer,
            content=request.content,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recommendation: {str(e)}"
        )


@app.put("/operator/recommendations/{recommendation_id}", tags=["Operator"])
async def update_operator_recommendation(
    recommendation_id: str,
    request: UpdateOperatorRecommendationRequest
):
    """Update existing operator recommendation"""
    from api.services.operator_recs import update_operator_rec
    try:
        result = update_operator_rec(
            recommendation_id=recommendation_id,
            title=request.title,
            description=request.description,
            category=request.category,
            topic=request.topic,
            rationale=request.rationale,
            operator_name=request.operator_name,
            disclaimer=request.disclaimer,
            content=request.content,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recommendation: {str(e)}"
        )


@app.delete("/operator/recommendations/{recommendation_id}", tags=["Operator"])
async def delete_operator_recommendation(recommendation_id: str, operator_name: str):
    """Soft-delete operator recommendation"""
    from api.services.operator_recs import delete_operator_rec
    try:
        result = delete_operator_rec(recommendation_id, operator_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete recommendation: {str(e)}"
        )


@app.post("/operator/recommendations/{recommendation_id}/override", tags=["Operator"])
async def override_auto_recommendation(
    recommendation_id: str,
    request: OverrideRecommendationRequest
):
    """Override an auto-generated recommendation"""
    from api.services.operator_recs import override_auto_rec
    try:
        result = override_auto_rec(
            user_id=request.user_id,
            original_rec_id=recommendation_id,
            rec_type=request.type,
            title=request.title,
            description=request.description,
            category=request.category,
            topic=request.topic,
            rationale=request.rationale,
            operator_name=request.operator_name,
            disclaimer=request.disclaimer,
            content=request.content,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to override recommendation: {str(e)}"
        )


@app.get("/operator/recommendations/bulk/{user_ids}", tags=["Operator"])
async def bulk_get_recommendations(user_ids: str):
    """Get recommendations for multiple users (comma-separated)"""
    from api.services.operator_recs import bulk_get_recs
    user_id_list = [uid.strip() for uid in user_ids.split(',')]
    return bulk_get_recs(user_id_list)


@app.post("/operator/recommendations/bulk/edit", tags=["Operator"])
async def bulk_edit_recommendations(request: BulkEditRequest):
    """Bulk edit multiple recommendations"""
    from api.services.operator_recs import bulk_edit_recs
    try:
        result = bulk_edit_recs(
            recommendation_ids=request.recommendation_ids,
            updates=request.updates,
            operator_name=request.operator_name
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk edit: {str(e)}"
        )


# Evaluation endpoint
@app.get("/eval/summary", response_model=EvaluationSummaryResponse, tags=["Evaluation"])
async def get_evaluation_summary():
    """Get system evaluation metrics"""
    # TODO: Implement in PR #8 (Evaluation Harness)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evaluation will be implemented in PR #8",
    )


# Development information endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SpendSense MVP V2 API",
        "version": "0.1.0",
        "status": "PR #1: Project Setup & Data Foundation",
        "docs": "/docs",
        "health": "/health",
        "note": "Most endpoints will be implemented in subsequent PRs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
