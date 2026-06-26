"""Playlists API Router"""
import json
import secrets
import uuid as uuid_lib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import get_db
from app.models.user import User
from app.models.playlist import Playlist, PlaylistTrack
from app.models.track import Track
from app.models.recommendation import RecommendationSession, RecommendationTrack
from app.dependencies import get_current_user

router = APIRouter(prefix="/playlists", tags=["Playlists"])


class CreatePlaylistRequest(BaseModel):
    session_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    is_public: bool = False


@router.post("", status_code=201)
async def create_playlist(
    payload: CreatePlaylistRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = Playlist(
        user_id=current_user.id,
        session_id=payload.session_id,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
        share_token=secrets.token_urlsafe(16) if payload.is_public else None,
    )

    # If session_id provided, copy tracks from recommendation session
    if payload.session_id:
        session_result = await db.execute(
            select(RecommendationSession).where(
                RecommendationSession.id == payload.session_id,
                RecommendationSession.user_id == current_user.id,
            )
        )
        session = session_result.scalar_one_or_none()
        if session:
            playlist.mood_context = session.primary_mood
            playlist.activity_context = session.activity_type

    db.add(playlist)
    await db.flush()

    # Copy recommendation tracks if session provided
    if payload.session_id:
        rec_result = await db.execute(
            select(RecommendationTrack).where(
                RecommendationTrack.session_id == payload.session_id
            ).order_by(RecommendationTrack.rank_position)
        )
        rec_tracks = rec_result.scalars().all()

        for i, rt in enumerate(rec_tracks):
            pt = PlaylistTrack(
                playlist_id=playlist.id,
                track_id=rt.track_id,
                position=i + 1,
            )
            db.add(pt)

        playlist.track_count = len(rec_tracks)

    await db.commit()
    await db.refresh(playlist)

    return {
        "playlist_id": str(playlist.id),
        "name": playlist.name,
        "track_count": playlist.track_count,
        "share_token": playlist.share_token,
        "message": "Playlist created successfully",
    }


@router.get("")
async def list_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(desc(Playlist.created_at))
    )
    playlists = result.scalars().all()

    return [
        {
            "playlist_id": str(p.id),
            "name": p.name,
            "description": p.description,
            "mood_context": p.mood_context,
            "activity_context": p.activity_context,
            "track_count": p.track_count,
            "is_public": p.is_public,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in playlists
    ]


@router.get("/{playlist_id}")
async def get_playlist(
    playlist_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist).where(
            Playlist.id == playlist_id,
            Playlist.user_id == current_user.id,
        )
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Get tracks
    tracks_result = await db.execute(
        select(PlaylistTrack, Track)
        .join(Track, PlaylistTrack.track_id == Track.id)
        .where(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.position)
    )
    track_rows = tracks_result.all()

    tracks = [
        {
            "position": pt.position,
            "spotify_id": t.spotify_id,
            "title": t.title,
            "artist": t.artist,
            "album": t.album,
            "duration_ms": t.duration_ms,
            "album_art_url": t.album_art_url,
            "spotify_url": t.spotify_url,
            "preview_url": t.preview_url,
        }
        for pt, t in track_rows
    ]

    return {
        "playlist_id": str(playlist.id),
        "name": playlist.name,
        "description": playlist.description,
        "mood_context": playlist.mood_context,
        "activity_context": playlist.activity_context,
        "track_count": playlist.track_count,
        "is_public": playlist.is_public,
        "tracks": tracks,
    }


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist).where(
            Playlist.id == playlist_id,
            Playlist.user_id == current_user.id,
        )
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    await db.delete(playlist)
    await db.commit()
    return {"message": "Playlist deleted"}
