"""
FastAPI application for SpendSense MVP V2.
REST endpoints for user and operator interfaces.
"""

from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    HealthResponse,
    ConsentRequest,
    UserProfileResponse,
    UserRecommendationsResponse,
    FeedbackRequest,
    OperatorReviewRequest,
    EvaluationSummaryResponse
)


# Initialize FastAPI app
app = FastAPI(
    title="SpendSense MVP V2",
    description="Explainable, consent-aware financial behavior analysis platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="0.1.0"
    )


# User endpoints
@app.post("/users", tags=["Users"], status_code=status.HTTP_201_CREATED)
async def create_user(user_data: dict):
    """Create a new user (placeholder for PR #1)"""
    # TODO: Implement in future PR when user creation is needed
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation will be implemented in a future PR"
    )


@app.post("/consent", tags=["Users"])
async def update_consent(request: ConsentRequest):
    """Grant or revoke user consent"""
    # TODO: Implement consent management in PR #5 (Guardrails)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Consent management will be implemented in PR #5"
    )


@app.get("/profile/{user_id}", response_model=UserProfileResponse, tags=["Users"])
async def get_user_profile(user_id: str):
    """Get user profile with persona and behavioral signals"""
    # TODO: Implement in PR #3 (Personas)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User profile will be implemented in PR #3"
    )


@app.get("/recommendations/{user_id}", response_model=UserRecommendationsResponse, tags=["Users"])
async def get_recommendations(user_id: str):
    """Get personalized recommendations for a user"""
    # TODO: Implement in PR #4 (Recommendations)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Recommendations will be implemented in PR #4"
    )


@app.post("/feedback", tags=["Users"])
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on a recommendation"""
    # TODO: Implement feedback tracking in future PR
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feedback will be implemented in a future PR"
    )


# Operator endpoints
@app.get("/operator/review", tags=["Operator"])
async def get_pending_reviews():
    """Get recommendations pending operator review"""
    # TODO: Implement in PR #7 (Operator Dashboard)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Operator review will be implemented in PR #7"
    )


@app.post("/operator/review", tags=["Operator"])
async def submit_review(request: OperatorReviewRequest):
    """Submit operator review decision"""
    # TODO: Implement in PR #7 (Operator Dashboard)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Operator review will be implemented in PR #7"
    )


# Evaluation endpoint
@app.get("/eval/summary", response_model=EvaluationSummaryResponse, tags=["Evaluation"])
async def get_evaluation_summary():
    """Get system evaluation metrics"""
    # TODO: Implement in PR #8 (Evaluation Harness)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evaluation will be implemented in PR #8"
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
        "note": "Most endpoints will be implemented in subsequent PRs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
