"""SQLAlchemy ORM Models — Tracks (Music Metadata Cache)"""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    album = Column(String(500))
    duration_ms = Column(Integer)
    preview_url = Column(String(500))
    spotify_url = Column(String(500))
    album_art_url = Column(String(500))

    # Spotify Audio Features
    tempo = Column(Float)
    energy = Column(Float, index=True)
    valence = Column(Float, index=True)
    danceability = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    speechiness = Column(Float)
    loudness = Column(Float)
    liveness = Column(Float)
    key = Column(Integer)
    mode = Column(Integer)
    time_signature = Column(Integer)

    # Derived Features
    lyrics_sentiment = Column(Float)
    mood_tags = Column(Text)   # JSON string
    genres = Column(Text)      # JSON string

    features_fetched_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recommendation_tracks = relationship("RecommendationTrack", back_populates="track")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track")
