"""SQLAlchemy ORM Models — Feedback"""
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_sessions.id"), nullable=True)
    rec_track_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_tracks.id"), nullable=True)

    # Ratings
    overall_rating = Column(Integer)
    energy_match = Column(Integer)
    mood_match = Column(Integer)

    # Qualitative
    feedback_tags = Column(Text)   # JSON string list
    comment = Column(Text)

    # Outcome Assessment
    pre_mood = Column(String(50))
    post_mood = Column(String(50))
    mood_improved = Column(Boolean)
    goal_achieved = Column(Boolean)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback")
    session = relationship("RecommendationSession", back_populates="feedback")
    rec_track = relationship("RecommendationTrack", back_populates="feedback")
