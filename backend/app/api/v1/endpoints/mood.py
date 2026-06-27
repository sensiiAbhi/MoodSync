"""Mood Assessment API Router"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.mood_assessment import MoodAssessment
from app.schemas.mood import (
    MoodAssessmentRequest, MoodAssessmentResponse,
    MoodHistoryItem, CircumplexPosition
)
from app.ml.mood_classifier import mood_classifier
from app.dependencies import get_current_user

router = APIRouter(prefix="/mood", tags=["Mood Assessment"])


def _get_time_of_day(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


@router.post("/assess", response_model=MoodAssessmentResponse, status_code=201)
async def submit_assessment(
    payload: MoodAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a mood assessment and get classification result."""
    now = datetime.now(timezone.utc)
    classification = mood_classifier.classify(
        payload.energy_level,
        payload.stress_level,
        payload.focus_level,
        payload.motivation_level,
        payload.sleep_quality,
        payload.mental_fatigue,
        payload.social_mood,
    )

    wellbeing = mood_classifier.compute_wellbeing_score(
        payload.energy_level,
        payload.stress_level,
        payload.focus_level,
        payload.motivation_level,
        payload.sleep_quality,
        payload.mental_fatigue,
        payload.social_mood,
    )

    assessment = MoodAssessment(
        user_id=current_user.id,
        energy_level=payload.energy_level,
        stress_level=payload.stress_level,
        focus_level=payload.focus_level,
        motivation_level=payload.motivation_level,
        sleep_quality=payload.sleep_quality,
        mental_fatigue=payload.mental_fatigue,
        social_mood=payload.social_mood,
        primary_mood=classification.primary_mood,
        mood_valence=classification.mood_valence,
        mood_arousal=classification.mood_arousal,
        classification_confidence=classification.confidence,
        assessment_type=payload.assessment_type,
        time_of_day=_get_time_of_day(now.hour),
        day_of_week=now.weekday(),
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    next_steps = {
        "stressed": "Let's find calming, focused music to help reduce your stress.",
        "anxious": "We'll find grounding, soothing music to ease your anxiety.",
        "burned_out": "Restorative, gentle music can help you recover energy.",
        "sleepy": "Calming music will help you wind down comfortably.",
        "energetic": "Great energy! Let's find music that matches your vibe.",
        "motivated": "You're ready to go! High-energy music will keep you in the zone.",
        "calm": "Music to help you maintain your peaceful state.",
        "focused": "Instrumental music will support your focus flow.",
        "relaxed": "Easy-going music to complement your relaxed mood.",
    }

    return MoodAssessmentResponse(
        assessment_id=assessment.id,
        primary_mood=classification.primary_mood,
        mood_valence=classification.mood_valence,
        mood_arousal=classification.mood_arousal,
        classification_confidence=classification.confidence,
        mood_description=classification.description,
        secondary_mood=classification.secondary_mood,
        recommended_next_step=next_steps.get(
            classification.primary_mood,
            "Let's find the perfect music for your current state."
        ),
        circumplex_position=CircumplexPosition(
            valence=classification.mood_valence,
            arousal=classification.mood_arousal,
            quadrant=classification.circumplex_quadrant,
        ),
        wellbeing_score=wellbeing,
    )


@router.get("/current")
async def get_current_assessment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's most recent mood assessment."""
    result = await db.execute(
        select(MoodAssessment)
        .where(MoodAssessment.user_id == current_user.id)
        .order_by(desc(MoodAssessment.assessed_at))
        .limit(1)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found. Please complete a mood check-in.")

    return {
        "assessment_id": str(assessment.id),
        "primary_mood": assessment.primary_mood,
        "mood_valence": assessment.mood_valence,
        "mood_arousal": assessment.mood_arousal,
        "confidence": assessment.classification_confidence,
        "energy_level": assessment.energy_level,
        "stress_level": assessment.stress_level,
        "focus_level": assessment.focus_level,
        "assessed_at": assessment.assessed_at.isoformat(),
    }


@router.get("/assessments", response_model=List[MoodHistoryItem])
async def get_assessment_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's mood assessment history."""
    result = await db.execute(
        select(MoodAssessment)
        .where(MoodAssessment.user_id == current_user.id)
        .order_by(desc(MoodAssessment.assessed_at))
        .limit(min(limit, 100))
    )
    assessments = result.scalars().all()

    items = []
    for a in assessments:
        ws = mood_classifier.compute_wellbeing_score(
            a.energy_level, a.stress_level, a.focus_level,
            a.motivation_level, a.sleep_quality, a.mental_fatigue, a.social_mood
        )
        items.append(MoodHistoryItem(
            id=a.id,
            primary_mood=a.primary_mood,
            mood_valence=a.mood_valence or 0.0,
            mood_arousal=a.mood_arousal or 0.0,
            energy_level=a.energy_level,
            stress_level=a.stress_level,
            focus_level=a.focus_level,
            motivation_level=a.motivation_level,
            wellbeing_score=ws,
            assessed_at=a.assessed_at,
        ))

    return items


@router.get("/trends")
async def get_mood_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood trend data over a period."""
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(MoodAssessment)
        .where(
            MoodAssessment.user_id == current_user.id,
            MoodAssessment.assessed_at >= since
        )
        .order_by(MoodAssessment.assessed_at)
    )
    assessments = result.scalars().all()

    if not assessments:
        return {"period_days": days, "data_points": [], "message": "No data yet"}

    data_points = [
        {
            "date": a.assessed_at.strftime("%Y-%m-%d"),
            "primary_mood": a.primary_mood,
            "valence": a.mood_valence,
            "arousal": a.mood_arousal,
            "energy": a.energy_level,
            "stress": a.stress_level,
            "focus": a.focus_level,
            "wellbeing": mood_classifier.compute_wellbeing_score(
                a.energy_level, a.stress_level, a.focus_level,
                a.motivation_level, a.sleep_quality, a.mental_fatigue, a.social_mood
            ),
        }
        for a in assessments
    ]

    moods = [a.primary_mood for a in assessments]
    dominant_mood = max(set(moods), key=moods.count)

    avg_stress = sum(a.stress_level for a in assessments) / len(assessments)
    avg_energy = sum(a.energy_level for a in assessments) / len(assessments)
    avg_focus = sum(a.focus_level for a in assessments) / len(assessments)

    # Trend: compare first half vs second half
    mid = len(assessments) // 2
    if mid > 0:
        first_stress = sum(a.stress_level for a in assessments[:mid]) / mid
        second_stress = sum(a.stress_level for a in assessments[mid:]) / (len(assessments) - mid)
        stress_trend = "decreasing" if second_stress < first_stress - 0.5 else (
            "increasing" if second_stress > first_stress + 0.5 else "stable"
        )
        first_energy = sum(a.energy_level for a in assessments[:mid]) / mid
        second_energy = sum(a.energy_level for a in assessments[mid:]) / (len(assessments) - mid)
        energy_trend = "increasing" if second_energy > first_energy + 0.5 else (
            "decreasing" if second_energy < first_energy - 0.5 else "stable"
        )
    else:
        stress_trend = energy_trend = "stable"

    return {
        "period_days": days,
        "total_assessments": len(assessments),
        "data_points": data_points,
        "dominant_mood": dominant_mood,
        "avg_stress": round(avg_stress, 1),
        "avg_energy": round(avg_energy, 1),
        "avg_focus": round(avg_focus, 1),
        "stress_trend": stress_trend,
        "energy_trend": energy_trend,
    }
