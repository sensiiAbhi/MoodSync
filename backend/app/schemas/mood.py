"""Pydantic Schemas — Mood Assessment"""
from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
from datetime import datetime


class ConversationalAssessmentRequest(BaseModel):
    conversational_answers: dict
    assessment_type: str = "conversational"

class MoodAssessmentRequest(BaseModel):
    energy_level: int
    stress_level: int
    focus_level: int
    motivation_level: int
    sleep_quality: int
    mental_fatigue: int
    social_mood: int
    assessment_type: str = "full"

    @field_validator(
        "energy_level", "stress_level", "focus_level",
        "motivation_level", "sleep_quality", "mental_fatigue", "social_mood"
    )
    @classmethod
    def score_range(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("Score must be between 1 and 10")
        return v


class CircumplexPosition(BaseModel):
    valence: float
    arousal: float
    quadrant: str


class MoodAssessmentResponse(BaseModel):
    assessment_id: uuid.UUID
    primary_mood: str
    mood_valence: float
    mood_arousal: float
    classification_confidence: float
    mood_description: str
    secondary_mood: Optional[str]
    recommended_next_step: str
    circumplex_position: CircumplexPosition
    wellbeing_score: float

    class Config:
        from_attributes = True


class MoodHistoryItem(BaseModel):
    id: uuid.UUID
    primary_mood: str
    mood_valence: float
    mood_arousal: float
    energy_level: int
    stress_level: int
    focus_level: int
    motivation_level: int
    wellbeing_score: Optional[float] = None
    assessed_at: datetime

    class Config:
        from_attributes = True


class MoodTrendResponse(BaseModel):
    period_days: int
    data_points: list
    dominant_mood: str
    avg_stress: float
    avg_energy: float
    avg_focus: float
    stress_trend: str
    energy_trend: str
