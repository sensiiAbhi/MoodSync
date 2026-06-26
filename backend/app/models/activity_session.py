"""SQLAlchemy ORM Models — Activity Sessions"""
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ActivitySession(Base):
    __tablename__ = "activity_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("mood_assessments.id"), nullable=True)

    activity_type = Column(String(50), nullable=False)
    desired_outcome = Column(String(100))
    planned_duration_minutes = Column(Integer)
    actual_duration_minutes = Column(Integer)
    session_status = Column(String(20), default="active")
    productivity_rating = Column(Integer)
    notes = Column(Text)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="activity_sessions")
    assessment = relationship("MoodAssessment", back_populates="activity_sessions")
    recommendation_sessions = relationship("RecommendationSession", back_populates="activity_session")
