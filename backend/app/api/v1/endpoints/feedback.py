"""Feedback API Router"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User, UserProfile
from app.models.feedback import Feedback
from app.models.recommendation import RecommendationSession
from app.schemas.feedback import SessionFeedbackRequest, FeedbackResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/session", response_model=FeedbackResponse, status_code=201)
async def submit_session_feedback(
    payload: SessionFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a full recommendation session."""
    # Verify session belongs to user
    result = await db.execute(
        select(RecommendationSession).where(
            RecommendationSession.id == payload.session_id,
            RecommendationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Store feedback
    feedback = Feedback(
        user_id=current_user.id,
        session_id=payload.session_id,
        overall_rating=payload.overall_rating,
        energy_match=payload.energy_match,
        mood_match=payload.mood_match,
        feedback_tags=json.dumps(payload.feedback_tags or []),
        comment=payload.comment,
        pre_mood=payload.pre_mood,
        post_mood=payload.post_mood,
        mood_improved=payload.mood_improved,
        goal_achieved=payload.goal_achieved,
    )
    db.add(feedback)

    # Update session's avg rating
    session.avg_rating = float(payload.overall_rating)
    session.session_success = payload.goal_achieved

    # Update user streak
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    new_streak = 1
    if profile:
        profile.assessment_streak = (profile.assessment_streak or 0) + 1
        profile.total_sessions = (profile.total_sessions or 0) + 1
        new_streak = profile.assessment_streak

    await db.commit()

    return FeedbackResponse(
        feedback_id=feedback.id,
        message="Thank you! Your feedback helps improve future recommendations.",
        mood_improvement_detected=payload.mood_improved or False,
        new_streak_count=new_streak,
    )


@router.get("/effectiveness")
async def get_effectiveness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recommendation effectiveness metrics for the current user."""
    result = await db.execute(
        select(Feedback).where(Feedback.user_id == current_user.id)
    )
    feedbacks = result.scalars().all()

    if not feedbacks:
        return {
            "avg_rating": 0,
            "sessions_rated": 0,
            "goal_achievement_rate": 0,
            "mood_improvement_rate": 0,
            "message": "No feedback yet. Rate some sessions to see your stats!",
        }

    avg_rating = sum(f.overall_rating or 0 for f in feedbacks) / len(feedbacks)

    goal_achieved = [f for f in feedbacks if f.goal_achieved is True]
    mood_improved = [f for f in feedbacks if f.mood_improved is True]

    all_tags = []
    for f in feedbacks:
        if f.feedback_tags:
            try:
                all_tags.extend(json.loads(f.feedback_tags))
            except Exception:
                pass

    tag_counts: dict = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    positive_tags = ["helped_focus", "good_tempo", "perfect_match", "relaxing", "energizing"]
    negative_tags = ["too_energetic", "too_slow", "poor_match", "too_loud"]

    top_positive = [t for t in positive_tags if t in tag_counts][:3]
    top_negative = [t for t in negative_tags if t in tag_counts][:3]

    return {
        "avg_rating": round(avg_rating, 2),
        "sessions_rated": len(feedbacks),
        "goal_achievement_rate": round(len(goal_achieved) / len(feedbacks), 2),
        "mood_improvement_rate": round(len(mood_improved) / len(feedbacks), 2),
        "top_positive_tags": top_positive,
        "top_negative_tags": top_negative,
    }
