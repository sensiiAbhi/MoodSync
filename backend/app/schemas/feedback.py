"""Pydantic Schemas — Feedback"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
import uuid


class SessionFeedbackRequest(BaseModel):
    session_id: uuid.UUID
    overall_rating: int
    energy_match: Optional[int] = None
    mood_match: Optional[int] = None
    feedback_tags: Optional[List[str]] = None
    comment: Optional[str] = None
    pre_mood: Optional[str] = None
    post_mood: Optional[str] = None
    mood_improved: Optional[bool] = None
    goal_achieved: Optional[bool] = None

    @field_validator("overall_rating", "energy_match", "mood_match")
    @classmethod
    def rating_range(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackResponse(BaseModel):
    feedback_id: uuid.UUID
    message: str
    mood_improvement_detected: bool
    new_streak_count: int


class TrackFeedbackRequest(BaseModel):
    rec_track_id: uuid.UUID
    rating: int
    tags: Optional[List[str]] = None


class EffectivenessMetrics(BaseModel):
    avg_rating: float
    sessions_rated: int
    goal_achievement_rate: float
    mood_improvement_rate: float
    top_positive_tags: List[str]
    top_negative_tags: List[str]
