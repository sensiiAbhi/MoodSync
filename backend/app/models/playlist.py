"""SQLAlchemy ORM Models — Playlists"""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_sessions.id"), nullable=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    mood_context = Column(String(50))
    activity_context = Column(String(50))
    track_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    spotify_playlist_id = Column(String(100))
    share_token = Column(String(100), unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="playlists")
    session = relationship("RecommendationSession", back_populates="playlists")
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track", back_populates="playlist_tracks")
