"""Activities API Router"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import get_db
from app.models.user import User
from app.models.activity_session import ActivitySession
from app.dependencies import get_current_user

router = APIRouter(prefix="/activities", tags=["Activities"])


class StartActivityRequest(BaseModel):
    assessment_id: Optional[uuid.UUID] = None
    activity_type: str
    desired_outcome: Optional[str] = None
    planned_duration_minutes: Optional[int] = None


class EndActivityRequest(BaseModel):
    productivity_rating: Optional[int] = None
    notes: Optional[str] = None


@router.post("/start", status_code=201)
async def start_activity(
    payload: StartActivityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ActivitySession(
        user_id=current_user.id,
        assessment_id=payload.assessment_id,
        activity_type=payload.activity_type,
        desired_outcome=payload.desired_outcome,
        planned_duration_minutes=payload.planned_duration_minutes,
        session_status="active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": str(session.id),
        "activity_type": session.activity_type,
        "desired_outcome": session.desired_outcome,
        "started_at": session.started_at.isoformat(),
    }


@router.patch("/{session_id}/end")
async def end_activity(
    session_id: uuid.UUID,
    payload: EndActivityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ActivitySession).where(
            ActivitySession.id == session_id,
            ActivitySession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.now(timezone.utc)
    session.ended_at = now
    session.session_status = "completed"
    session.productivity_rating = payload.productivity_rating
    session.notes = payload.notes

    if session.started_at:
        duration = (now - session.started_at).total_seconds() / 60
        session.actual_duration_minutes = int(duration)

    await db.commit()
    return {"message": "Activity session ended", "session_id": str(session_id)}


@router.get("")
async def get_activities(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ActivitySession)
        .where(ActivitySession.user_id == current_user.id)
        .order_by(desc(ActivitySession.started_at))
        .limit(min(limit, 50))
    )
    sessions = result.scalars().all()

    return [
        {
            "session_id": str(s.id),
            "activity_type": s.activity_type,
            "desired_outcome": s.desired_outcome,
            "session_status": s.session_status,
            "planned_duration_minutes": s.planned_duration_minutes,
            "actual_duration_minutes": s.actual_duration_minutes,
            "productivity_rating": s.productivity_rating,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]


@router.get("/stats")
async def get_activity_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ActivitySession).where(ActivitySession.user_id == current_user.id)
    )
    sessions = result.scalars().all()

    dist: dict = {}
    for s in sessions:
        dist[s.activity_type] = dist.get(s.activity_type, 0) + 1

    total = len(sessions)
    return {
        "total_sessions": total,
        "activity_distribution": {k: round(v / max(total, 1), 2) for k, v in dist.items()},
        "most_common_activity": max(dist, key=dist.get) if dist else None,
    }
