"""SQLAlchemy ORM Models — Mood Assessments"""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MoodAssessment(Base):
    __tablename__ = "mood_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Raw Assessment Scores (1-10)
    energy_level = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    focus_level = Column(Integer, nullable=False)
    motivation_level = Column(Integer, nullable=False)
    sleep_quality = Column(Integer, nullable=False)
    mental_fatigue = Column(Integer, nullable=False)
    social_mood = Column(Integer, nullable=False)

    # Derived Classification
    primary_mood = Column(String(50), nullable=False)
    mood_valence = Column(Float)
    mood_arousal = Column(Float)
    classification_confidence = Column(Float)
    assessment_type = Column(String(20), default="full")

    # Time Context
    time_of_day = Column(String(20))
    day_of_week = Column(Integer)

    # Post-session data
    post_session_energy = Column(Integer)
    post_session_mood = Column(String(50))
    mood_improvement_score = Column(Float)

    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="mood_assessments")
    activity_sessions = relationship("ActivitySession", back_populates="assessment")
    recommendation_sessions = relationship("RecommendationSession", back_populates="assessment")
