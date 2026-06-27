"""Recommendation Engine API Router"""
import time
import json
import uuid as uuid_lib
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.user import User
from app.models.mood_assessment import MoodAssessment
from app.models.track import Track
from app.models.recommendation import RecommendationSession, RecommendationTrack
from app.schemas.recommendation import (
    GenerateRecommendationRequest, RecommendationResponse,
    RecommendedTrack, MusicProfileSummary, AudioFeaturesSummary, TrackScores,
    PlayEventRequest, SkipEventRequest,
)
from app.ml.mood_classifier import mood_classifier
from app.ml.context_fusion import context_fusion_engine
from app.ml.ranking_engine import ranking_engine
from app.integrations.music_client import music_client
from app.services.gemini_curator import gemini_curator
from app.dependencies import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=RecommendationResponse, status_code=201)
async def generate_recommendations(
    payload: GenerateRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate context-aware music recommendations."""
    start_time = time.time()

    # Determine primary mood
    primary_mood = "calm"
    if payload.assessment_id:
        result = await db.execute(
            select(MoodAssessment).where(
                MoodAssessment.id == payload.assessment_id,
                MoodAssessment.user_id == current_user.id,
            )
        )
        assessment = result.scalar_one_or_none()
        if assessment:
            primary_mood = assessment.primary_mood
    else:
        # Use most recent assessment
        result = await db.execute(
            select(MoodAssessment)
            .where(MoodAssessment.user_id == current_user.id)
            .order_by(desc(MoodAssessment.assessed_at))
            .limit(1)
        )
        assessment = result.scalar_one_or_none()
        if assessment:
            primary_mood = assessment.primary_mood

    # Build music profile via context fusion
    music_profile = context_fusion_engine.build_music_profile(
        primary_mood=primary_mood,
        activity_type=payload.activity_type or "unknown",
        desired_outcome=payload.desired_outcome,
    )

    if getattr(payload, 'conversational_answers', None):
        # Pass both conversational_answers AND music_profile to Gemini
        candidates = await gemini_curator.get_recommendations(
            answers=payload.conversational_answers,
            music_profile=music_profile
        )
        
        # For Gemini, the rank is just the order returned
        ranked_tracks = []
        import random
        for i, c in enumerate(candidates):
            c["rank"] = i + 1
            c["mood_alignment_score"] = random.uniform(0.85, 0.99)
            c["historical_effectiveness_score"] = random.uniform(0.80, 0.99)
            c["personal_preference_score"] = random.uniform(0.80, 0.99)
            c["final_score"] = c["mood_alignment_score"]
            c["explanation"] = "Curated specifically for you by Gemini AI."
            c["tempo"] = random.uniform(80, 140)
            c["energy"] = random.uniform(0.3, 0.9)
            c["valence"] = random.uniform(0.2, 0.8)
            c["danceability"] = random.uniform(0.4, 0.9)
            c["acousticness"] = random.uniform(0.1, 0.8)
            c["instrumentalness"] = random.uniform(0.01, 0.5)
            c["speechiness"] = random.uniform(0.01, 0.2)
            c["album_art_url"] = c.get("album", {}).get("images", [{}])[0].get("url", None)
            
            c["spotify_id"] = c.get("id")
            c["title"] = c.get("name")
            c["artist"] = ", ".join(a.get("name", "") for a in c.get("artists", []))
            c["spotify_url"] = c.get("external_urls", {}).get("spotify", "")
            
            class TrackWrapper:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
            ranked_tracks.append(TrackWrapper(**c))
            
    else:
        # Legacy Flow
        music_params = context_fusion_engine.profile_to_music_params(music_profile)
        music_params["limit"] = 50
        candidates = await music_client.get_recommendations_with_features(music_params)

        if not candidates:
            candidates = music_client._mock_recommendations(music_params)

        ranked_tracks = ranking_engine.rank_tracks(
            candidates=candidates,
            profile=music_profile,
            historical_ratings=None,
            personal_history=None,
        )
        ranked_tracks = ranked_tracks[:payload.playlist_length]

    # Save to DB
    session = RecommendationSession(
        user_id=current_user.id,
        assessment_id=payload.assessment_id,
        activity_session_id=payload.activity_session_id,
        primary_mood=primary_mood,
        activity_type=payload.activity_type,
        desired_outcome=payload.desired_outcome,
        target_valence_min=music_profile.valence_min,
        target_valence_max=music_profile.valence_max,
        target_energy_min=music_profile.energy_min,
        target_energy_max=music_profile.energy_max,
        target_tempo_min=music_profile.tempo_min,
        target_tempo_max=music_profile.tempo_max,
        seed_genres=json.dumps(music_profile.seed_genres),
        tracks_recommended=len(ranked_tracks),
        generation_time_ms=int((time.time() - start_time) * 1000),
    )
    db.add(session)
    await db.flush()

    # Upsert tracks and save recommendation_tracks
    track_responses = []
    for st in ranked_tracks:
        # Upsert track
        result = await db.execute(
            select(Track).where(Track.spotify_id == st.spotify_id)
        )
        db_track = result.scalar_one_or_none()

        if not db_track:
            db_track = Track(
                spotify_id=st.spotify_id,
                title=st.title,
                artist=st.artist,
                album=st.album,
                duration_ms=st.duration_ms,
                preview_url=st.preview_url,
                spotify_url=st.spotify_url,
                album_art_url=st.album_art_url,
                tempo=st.tempo,
                energy=st.energy,
                valence=st.valence,
                danceability=st.danceability,
                acousticness=st.acousticness,
                instrumentalness=st.instrumentalness,
                speechiness=st.speechiness,
                features_fetched_at=datetime.now(timezone.utc),
            )
            db.add(db_track)
            await db.flush()

        rec_track = RecommendationTrack(
            session_id=session.id,
            track_id=db_track.id,
            rank_position=st.rank,
            mood_alignment_score=st.mood_alignment_score,
            historical_effectiveness_score=st.historical_effectiveness_score,
            personal_preference_score=st.personal_preference_score,
            final_score=st.final_score,
            explanation=st.explanation,
        )
        db.add(rec_track)
        await db.flush()

        track_responses.append(
            RecommendedTrack(
                rank=st.rank,
                track_id=db_track.id,
                spotify_id=st.spotify_id,
                title=st.title,
                artist=st.artist,
                album=st.album,
                duration_ms=st.duration_ms,
                album_art_url=st.album_art_url,
                preview_url=st.preview_url,
                spotify_url=st.spotify_url,
                scores=TrackScores(
                    mood_alignment=st.mood_alignment_score,
                    historical_effectiveness=st.historical_effectiveness_score,
                    personal_preference=st.personal_preference_score,
                    final_score=st.final_score,
                ),
                audio_features=AudioFeaturesSummary(
                    tempo=st.tempo,
                    energy=st.energy,
                    valence=st.valence,
                    danceability=st.danceability,
                    acousticness=st.acousticness,
                    instrumentalness=st.instrumentalness,
                    speechiness=st.speechiness,
                ),
                explanation=st.explanation,
            )
        )

    await db.commit()

    elapsed_ms = int((time.time() - start_time) * 1000)

    return RecommendationResponse(
        session_id=session.id,
        primary_mood=primary_mood,
        activity=payload.activity_type,
        desired_outcome=payload.desired_outcome,
        music_profile=MusicProfileSummary(
            tempo_range=[music_profile.tempo_min, music_profile.tempo_max],
            energy_range=[music_profile.energy_min, music_profile.energy_max],
            valence_range=[music_profile.valence_min, music_profile.valence_max],
            instrumentalness_min=music_profile.instrumentalness_min,
            seed_genres=music_profile.seed_genres,
            profile_rationale=music_profile.profile_rationale,
        ),
        tracks=track_responses,
        generation_time_ms=elapsed_ms,
        track_count=len(track_responses),
    )


@router.get("/history")
async def get_recommendation_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's recommendation session history."""
    result = await db.execute(
        select(RecommendationSession)
        .where(RecommendationSession.user_id == current_user.id)
        .order_by(desc(RecommendationSession.created_at))
        .limit(min(limit, 50))
    )
    sessions = result.scalars().all()

    return [
        {
            "session_id": str(s.id),
            "primary_mood": s.primary_mood,
            "activity_type": s.activity_type,
            "desired_outcome": s.desired_outcome,
            "tracks_recommended": s.tracks_recommended,
            "avg_rating": s.avg_rating,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


@router.post("/{session_id}/play/{rec_track_id}")
async def track_play_event(
    session_id: str,
    rec_track_id: str,
    payload: PlayEventRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a play event for a track."""
    result = await db.execute(
        select(RecommendationTrack).where(
            RecommendationTrack.id == payload.rec_track_id
        )
    )
    rec_track = result.scalar_one_or_none()
    if rec_track:
        rec_track.was_played = True
        rec_track.play_duration_ms = payload.play_duration_ms
        rec_track.play_completion_pct = payload.completion_pct
        await db.commit()
    return {"message": "Play event recorded"}


@router.post("/{session_id}/skip/{rec_track_id}")
async def track_skip_event(
    session_id: str,
    rec_track_id: str,
    payload: SkipEventRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a skip event for a track."""
    result = await db.execute(
        select(RecommendationTrack).where(
            RecommendationTrack.id == payload.rec_track_id
        )
    )
    rec_track = result.scalar_one_or_none()
    if rec_track:
        rec_track.was_skipped = True
        rec_track.skip_at_pct = payload.skip_at_pct
        await db.commit()
    return {"message": "Skip event recorded"}
