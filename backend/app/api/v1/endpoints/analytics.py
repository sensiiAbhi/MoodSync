"""Analytics Dashboard API Router"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User, UserProfile
from app.models.mood_assessment import MoodAssessment
from app.models.recommendation import RecommendationSession
from app.models.feedback import Feedback
from app.models.activity_session import ActivitySession
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full analytics dashboard — aggregated data for the last 30 days."""
    since = datetime.now(timezone.utc) - timedelta(days=30)

    # Mood data
    mood_result = await db.execute(
        select(MoodAssessment)
        .where(
            MoodAssessment.user_id == current_user.id,
            MoodAssessment.assessed_at >= since
        )
        .order_by(MoodAssessment.assessed_at)
    )
    assessments = mood_result.scalars().all()

    mood_dist: dict = {}
    for a in assessments:
        mood_dist[a.primary_mood] = mood_dist.get(a.primary_mood, 0) + 1

    total_moods = len(assessments) or 1
    mood_distribution = {k: round(v / total_moods, 2) for k, v in mood_dist.items()}
    dominant_mood = max(mood_dist, key=mood_dist.get) if mood_dist else "unknown"

    # Session data
    session_result = await db.execute(
        select(RecommendationSession)
        .where(
            RecommendationSession.user_id == current_user.id,
            RecommendationSession.created_at >= since,
        )
    )
    sessions = session_result.scalars().all()
    total_sessions = len(sessions)

    # Activity distribution
    activity_dist: dict = {}
    for s in sessions:
        activity_dist[s.activity_type] = activity_dist.get(s.activity_type, 0) + 1

    total_acts = len(sessions) or 1
    activity_distribution = {
        k: round(v / total_acts, 2) for k, v in activity_dist.items()
    }

    # Feedback metrics
    fb_result = await db.execute(
        select(Feedback).where(Feedback.user_id == current_user.id)
    )
    feedbacks = fb_result.scalars().all()
    avg_rating = (
        round(sum(f.overall_rating or 0 for f in feedbacks) / len(feedbacks), 2)
        if feedbacks else 0
    )
    goal_rate = (
        round(sum(1 for f in feedbacks if f.goal_achieved) / len(feedbacks), 2)
        if feedbacks else 0
    )
    mood_improve_rate = (
        round(sum(1 for f in feedbacks if f.mood_improved) / len(feedbacks), 2)
        if feedbacks else 0
    )

    # Profile streak
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    streak = profile.assessment_streak if profile else 0

    # Genre stats from sessions
    top_genres: list = []
    for s in sessions:
        if s.seed_genres:
            import json
            try:
                genres = json.loads(s.seed_genres)
                top_genres.extend(genres)
            except Exception:
                pass

    genre_count: dict = {}
    for g in top_genres:
        genre_count[g] = genre_count.get(g, 0) + 1

    top_3_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:3]

    # Trend computation (simple)
    if len(assessments) >= 4:
        mid = len(assessments) // 2
        first_half = assessments[:mid]
        second_half = assessments[mid:]
        avg_stress_first = sum(a.stress_level for a in first_half) / len(first_half)
        avg_stress_second = sum(a.stress_level for a in second_half) / len(second_half)
        avg_energy_first = sum(a.energy_level for a in first_half) / len(first_half)
        avg_energy_second = sum(a.energy_level for a in second_half) / len(second_half)

        avg_stress_trend = (
            "decreasing" if avg_stress_second < avg_stress_first - 0.5 else
            ("increasing" if avg_stress_second > avg_stress_first + 0.5 else "stable")
        )
        avg_energy_trend = (
            "increasing" if avg_energy_second > avg_energy_first + 0.5 else
            ("decreasing" if avg_energy_second < avg_energy_first - 0.5 else "stable")
        )
    else:
        avg_stress_trend = avg_energy_trend = "stable"

    avg_stress = round(sum(a.stress_level for a in assessments) / total_moods, 1)
    avg_energy = round(sum(a.energy_level for a in assessments) / total_moods, 1)

    return {
        "period": "last_30_days",
        "mood_summary": {
            "dominant_mood": dominant_mood,
            "mood_distribution": mood_distribution,
            "total_assessments": len(assessments),
            "avg_stress": avg_stress,
            "avg_energy": avg_energy,
            "avg_stress_trend": avg_stress_trend,
            "avg_energy_trend": avg_energy_trend,
        },
        "listening_summary": {
            "total_sessions": total_sessions,
            "top_genres": [g for g, _ in top_3_genres],
        },
        "recommendation_effectiveness": {
            "avg_rating": avg_rating,
            "sessions_rated": len(feedbacks),
            "goal_achievement_rate": goal_rate,
            "mood_improvement_rate": mood_improve_rate,
        },
        "activity_distribution": activity_distribution,
        "streaks": {
            "current_streak": streak,
        },
    }


@router.get("/mood-calendar")
async def get_mood_calendar(
    weeks: int = 12,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood data for calendar heatmap (GitHub-style)."""
    since = datetime.now(timezone.utc) - timedelta(weeks=weeks)

    result = await db.execute(
        select(MoodAssessment)
        .where(
            MoodAssessment.user_id == current_user.id,
            MoodAssessment.assessed_at >= since,
        )
        .order_by(MoodAssessment.assessed_at)
    )
    assessments = result.scalars().all()

    from app.ml.mood_classifier import mood_classifier
    calendar = {}
    for a in assessments:
        date_key = a.assessed_at.strftime("%Y-%m-%d")
        ws = mood_classifier.compute_wellbeing_score(
            a.energy_level, a.stress_level, a.focus_level,
            a.motivation_level, a.sleep_quality, a.mental_fatigue, a.social_mood
        )
        calendar[date_key] = {
            "mood": a.primary_mood,
            "wellbeing": ws,
            "valence": a.mood_valence,
        }

    return {"calendar": calendar, "weeks": weeks}


@router.get("/weekly-report")
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get weekly mood and listening summary."""
    since = datetime.now(timezone.utc) - timedelta(days=7)

    mood_result = await db.execute(
        select(MoodAssessment)
        .where(MoodAssessment.user_id == current_user.id, MoodAssessment.assessed_at >= since)
    )
    assessments = mood_result.scalars().all()

    session_result = await db.execute(
        select(RecommendationSession)
        .where(RecommendationSession.user_id == current_user.id, RecommendationSession.created_at >= since)
    )
    sessions = session_result.scalars().all()

    moods = [a.primary_mood for a in assessments]
    dominant = max(set(moods), key=moods.count) if moods else "N/A"

    return {
        "week_summary": {
            "check_ins": len(assessments),
            "listening_sessions": len(sessions),
            "dominant_mood": dominant,
            "avg_stress": round(sum(a.stress_level for a in assessments) / max(len(assessments), 1), 1),
            "avg_energy": round(sum(a.energy_level for a in assessments) / max(len(assessments), 1), 1),
        }
    }
