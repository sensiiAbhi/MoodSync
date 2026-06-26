"""SQLAlchemy ORM Models — Users & Profiles"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    spotify_id = Column(String(100), unique=True)
    spotify_access_token = Column(Text)
    spotify_refresh_token = Column(Text)
    spotify_token_expires = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mood_assessments = relationship("MoodAssessment", back_populates="user", cascade="all, delete-orphan")
    activity_sessions = relationship("ActivitySession", back_populates="user", cascade="all, delete-orphan")
    recommendation_sessions = relationship("RecommendationSession", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    preference_weights = relationship("UserPreferenceWeights", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age_range = Column(String(20))
    occupation = Column(String(100))
    timezone = Column(String(50), default="UTC")
    preferred_genres = Column(Text)  # JSON string list
    music_familiarity = Column(Integer)
    assessment_streak = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    onboarding_completed = Column(Boolean, default=False)
    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False)
    device_info = Column(String(255))
    ip_address = Column(String(45))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")
