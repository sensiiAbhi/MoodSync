"""SQLAlchemy ORM Models — Recommendation Sessions & Tracks"""
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("mood_assessments.id"), nullable=True)
    activity_session_id = Column(UUID(as_uuid=True), ForeignKey("activity_sessions.id"), nullable=True)

    # Input Context
    primary_mood = Column(String(50), nullable=False)
    activity_type = Column(String(50), nullable=False)
    desired_outcome = Column(String(100))

    # Music Profile Used
    target_valence_min = Column(Float)
    target_valence_max = Column(Float)
    target_energy_min = Column(Float)
    target_energy_max = Column(Float)
    target_tempo_min = Column(Float)
    target_tempo_max = Column(Float)
    seed_genres = Column(Text)   # JSON string

    # Results
    tracks_recommended = Column(Integer)
    algorithm_version = Column(String(20), default="1.0")
    generation_time_ms = Column(Integer)

    # Effectiveness Metrics
    avg_rating = Column(Float)
    completion_rate = Column(Float)
    session_success = Column(Boolean)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="recommendation_sessions")
    assessment = relationship("MoodAssessment", back_populates="recommendation_sessions")
    activity_session = relationship("ActivitySession", back_populates="recommendation_sessions")
    recommendation_tracks = relationship("RecommendationTrack", back_populates="session", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="session")
    playlists = relationship("Playlist", back_populates="session")


class RecommendationTrack(Base):
    __tablename__ = "recommendation_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_sessions.id", ondelete="CASCADE"), nullable=False)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=False)
    rank_position = Column(Integer, nullable=False)

    mood_alignment_score = Column(Float)
    historical_effectiveness_score = Column(Float)
    personal_preference_score = Column(Float)
    final_score = Column(Float)
    explanation = Column(Text)

    # Listening Data
    was_played = Column(Boolean, default=False)
    play_duration_ms = Column(Integer)
    play_completion_pct = Column(Float)
    was_skipped = Column(Boolean, default=False)
    skip_at_pct = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("RecommendationSession", back_populates="recommendation_tracks")
    track = relationship("Track", back_populates="recommendation_tracks")
    feedback = relationship("Feedback", back_populates="rec_track")


class UserPreferenceWeights(Base):
    __tablename__ = "user_preference_weights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    mas_weight = Column(Float, default=0.45)
    hes_weight = Column(Float, default=0.30)
    pps_weight = Column(Float, default=0.25)

    tempo_sensitivity = Column(Float, default=1.0)
    energy_sensitivity = Column(Float, default=1.0)
    valence_sensitivity = Column(Float, default=1.0)
    instrumentalness_preference = Column(Float, default=0.5)

    genre_affinity = Column(Text, default="{}")  # JSON string
    model_version = Column(String(20))
    last_trained_at = Column(DateTime(timezone=True))
    training_samples = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="preference_weights")
