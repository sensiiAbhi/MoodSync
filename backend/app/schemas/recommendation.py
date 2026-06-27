"""Pydantic Schemas — Recommendations"""
from pydantic import BaseModel
from typing import Optional, List
import uuid


class GenerateRecommendationRequest(BaseModel):
    assessment_id: Optional[uuid.UUID] = None
    activity_session_id: Optional[uuid.UUID] = None
    activity_type: str
    desired_outcome: Optional[str] = None
    playlist_length: int = 25
    language_preference: str = "English"


class AudioFeaturesSummary(BaseModel):
    tempo: float
    energy: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    speechiness: float


class TrackScores(BaseModel):
    mood_alignment: float
    historical_effectiveness: float
    personal_preference: float
    final_score: float


class RecommendedTrack(BaseModel):
    rank: int
    track_id: Optional[uuid.UUID] = None
    spotify_id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    album_art_url: Optional[str]
    preview_url: Optional[str]
    spotify_url: str
    scores: TrackScores
    audio_features: AudioFeaturesSummary
    explanation: str


class MusicProfileSummary(BaseModel):
    tempo_range: List[float]
    energy_range: List[float]
    valence_range: List[float]
    instrumentalness_min: float
    seed_genres: List[str]
    profile_rationale: str


class RecommendationResponse(BaseModel):
    session_id: uuid.UUID
    primary_mood: str
    activity: str
    desired_outcome: Optional[str]
    music_profile: MusicProfileSummary
    tracks: List[RecommendedTrack]
    generation_time_ms: int
    track_count: int


class PlayEventRequest(BaseModel):
    rec_track_id: uuid.UUID
    play_duration_ms: Optional[int] = None
    completion_pct: Optional[float] = None


class SkipEventRequest(BaseModel):
    rec_track_id: uuid.UUID
    skip_at_pct: Optional[float] = None
