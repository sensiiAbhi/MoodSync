"""
MoodSync Spotify API Client
Handles all Spotify Web API communication including:
- Client Credentials auth (for track lookup, recommendations)
- User OAuth (for playlist creation, personal library)
- Audio features fetching and caching
"""
from __future__ import annotations
import base64
import time
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

SPOTIFY_API_BASE = "https://api.spotify.com/v1"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"


class SpotifyClient:
    """Async Spotify Web API client with auto-token refresh."""

    def __init__(self):
        self._client_token: Optional[str] = None
        self._client_token_expires: float = 0
        self._http = httpx.AsyncClient(timeout=10.0)

    # ─────────────────────── AUTH ───────────────────────

    async def _get_client_token(self) -> str:
        """Get or refresh Client Credentials token."""
        if self._client_token and time.time() < self._client_token_expires - 60:
            return self._client_token

        credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()

        resp = await self._http.post(
            SPOTIFY_AUTH_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        data = resp.json()
        self._client_token = data["access_token"]
        self._client_token_expires = time.time() + data["expires_in"]
        return self._client_token

    async def _headers(self, user_token: Optional[str] = None) -> Dict[str, str]:
        token = user_token or await self._get_client_token()
        return {"Authorization": f"Bearer {token}"}

    # ─────────────────────── RECOMMENDATIONS ───────────────────────

    async def get_recommendations(
        self,
        spotify_params: Dict[str, Any],
        user_token: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch track recommendations using iTunes Search API!
        (Bypasses Spotify's strict Premium-only API restrictions).
        Maps the iTunes response perfectly to the Spotify schema so the frontend
        doesn't break.
        """
        # Build a search query from the seed genres
        genres = spotify_params.get("seed_genres", "").split(",")
        valid_genres = [g.strip() for g in genres if g.strip()]
        
        query = "+".join(valid_genres[:2]) if valid_genres else "mood"
        limit = min(int(spotify_params.get("limit", 20)), 50)

        # Hit the free iTunes API (No auth needed!)
        resp = await self._http.get(
            "https://itunes.apple.com/search",
            params={"term": query, "entity": "song", "limit": limit},
        )
        
        if resp.status_code != 200:
            err_msg = f"iTunes API Error {resp.status_code}: {resp.text}"
            return self._mock_recommendations(spotify_params, err_msg)

        data = resp.json()
        results = data.get("results", [])
                
        if not results:
            # Fallback to broader search
            fallback_resp = await self._http.get(
                "https://itunes.apple.com/search",
                params={"term": "pop", "entity": "song", "limit": limit},
            )
            if fallback_resp.status_code == 200:
                results = fallback_resp.json().get("results", [])

        if not results:
            return self._mock_recommendations(spotify_params, "Error: iTunes returned 0 tracks")
            
        # Map iTunes schema to Spotify schema
        tracks = []
        for item in results:
            tracks.append({
                "id": str(item.get("trackId")),
                "name": item.get("trackName", "Unknown Track"),
                "artists": [{"name": item.get("artistName", "Unknown Artist")}],
                "album": {
                    "name": item.get("collectionName", "Unknown Album"),
                    "images": [{"url": item.get("artworkUrl100", "").replace("100x100bb", "300x300bb")}]
                },
                "duration_ms": item.get("trackTimeMillis", 180000),
                "preview_url": item.get("previewUrl"),
                "external_urls": {"spotify": item.get("trackViewUrl", "#")},
            })
            
        return tracks

    # ─────────────────────── AUDIO FEATURES (SIMULATED) ───────────────────────

    async def get_audio_features(
        self,
        track_ids: List[str],
        user_token: Optional[str] = None,
    ) -> Dict[str, Dict]:
        """
        Audio features API was deprecated by Spotify.
        We now simulate these features dynamically based on the ML engine targets.
        """
        return {}

    # ─────────────────────── TRACK LOOKUP ───────────────────────

    async def get_tracks(
        self,
        track_ids: List[str],
        user_token: Optional[str] = None,
    ) -> List[Dict]:
        """Fetch full track metadata for a list of IDs."""
        if not settings.SPOTIFY_CLIENT_ID or not track_ids:
            return []

        headers = await self._headers(user_token)
        results = []

        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            resp = await self._http.get(
                f"{SPOTIFY_API_BASE}/tracks",
                headers=headers,
                params={"ids": ",".join(batch)},
            )
            if resp.status_code == 200:
                results.extend(resp.json().get("tracks", []))

        return results

    # ─────────────────────── MERGED RECOMMENDATIONS ───────────────────────

    async def get_recommendations_with_features(
        self,
        spotify_params: Dict[str, Any],
        user_token: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch tracks from local songs_db.json, filter by language,
        and link them to a YouTube search so the user can easily play them.
        """
        import json
        import os
        from urllib.parse import quote_plus
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "songs_db.json")
        try:
            with open(db_path, "r") as f:
                local_tracks = json.load(f)
        except Exception as e:
            print(f"Error loading songs_db.json: {e}")
            local_tracks = []

        language_pref = spotify_params.get("language_preference", "Any")
        
        # Filter tracks by language if not 'Any'
        if language_pref != "Any":
            filtered_tracks = [t for t in local_tracks if t.get("language") == language_pref]
        else:
            filtered_tracks = local_tracks

        # Map to Spotify schema but link to YouTube search!
        merged = []
        for item in filtered_tracks:
            track_name = item.get("name", "Unknown Track")
            artist_name = item.get("artist", "Unknown Artist")
            
            # Create a YouTube search link
            yt_search = f"https://www.youtube.com/results?search_query={quote_plus(track_name + ' ' + artist_name)}"
            
            merged.append({
                "id": str(item.get("id")),
                "name": track_name,
                "artists": [{"name": artist_name}],
                "album": {
                    "name": item.get("album", "Unknown Album"),
                    "images": [{"url": "https://placehold.co/300x300/1e1e24/7c3aed?text=Album+Art"}]
                },
                "duration_ms": 180000,
                "preview_url": None, 
                "external_urls": {"spotify": yt_search}, # Point to YouTube!
                "audio_features": {
                    "tempo": item.get("tempo", 120.0),
                    "energy": item.get("energy", 0.5),
                    "valence": item.get("valence", 0.5),
                    "danceability": item.get("danceability", 0.5),
                    "acousticness": item.get("acousticness", 0.5),
                    "instrumentalness": item.get("instrumentalness", 0.1),
                    "speechiness": item.get("speechiness", 0.1),
                    "loudness": -6.0,
                    "liveness": item.get("liveness", 0.2),
                    "key": 0,
                    "mode": 1,
                    "time_signature": 4,
                }
            })
            
        return merged

    # ─────────────────────── SEARCH ───────────────────────

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
        user_token: Optional[str] = None,
    ) -> List[Dict]:
        """Search for tracks by query string."""
        if not settings.SPOTIFY_CLIENT_ID:
            return []

        headers = await self._headers(user_token)
        resp = await self._http.get(
            f"{SPOTIFY_API_BASE}/search",
            headers=headers,
            params={"q": query, "type": "track", "limit": limit},
        )
        if resp.status_code == 200:
            return resp.json().get("tracks", {}).get("items", [])
        return []

    # ─────────────────────── PLAYLIST EXPORT ───────────────────────

    async def create_playlist(
        self,
        user_spotify_id: str,
        name: str,
        description: str,
        public: bool,
        user_token: str,
    ) -> Optional[str]:
        """Create a Spotify playlist for the user. Returns playlist ID."""
        headers = await self._headers(user_token)
        headers["Content-Type"] = "application/json"

        resp = await self._http.post(
            f"{SPOTIFY_API_BASE}/users/{user_spotify_id}/playlists",
            headers=headers,
            json={"name": name, "description": description, "public": public},
        )
        if resp.status_code == 201:
            return resp.json().get("id")
        return None

    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        spotify_track_uris: List[str],
        user_token: str,
    ) -> bool:
        """Add tracks to a Spotify playlist."""
        headers = await self._headers(user_token)
        headers["Content-Type"] = "application/json"

        # Max 100 per request
        for i in range(0, len(spotify_track_uris), 100):
            batch = spotify_track_uris[i:i+100]
            resp = await self._http.post(
                f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
                headers=headers,
                json={"uris": batch},
            )
            if resp.status_code not in (200, 201):
                return False

        return True

    # ─────────────────────── MOCK DATA (dev mode) ───────────────────────

    def _mock_recommendations(self, params: Dict, error_msg: str = "Spotify API not configured") -> List[Dict]:
        """Return realistic mock tracks when Spotify API is not configured or fails."""
        mock_tracks = [
            {
                "id": f"mock_{i:04d}",
                "name": error_msg if i == 0 else name,
                "artists": [{"name": artist}],
                "album": {"name": album, "images": [{"url": f"https://picsum.photos/seed/{i+10}/300/300"}]},
                "duration_ms": 200000 + i * 5000,
                "preview_url": None,
                "external_urls": {"spotify": f"https://open.spotify.com/track/mock_{i:04d}"},
                "audio_features": {
                    "tempo": tempo,
                    "energy": energy,
                    "valence": valence,
                    "danceability": dance,
                    "acousticness": acoustic,
                    "instrumentalness": inst,
                    "speechiness": speech,
                    "loudness": -8.0,
                    "liveness": 0.1,
                    "key": 5,
                    "mode": 1,
                    "time_signature": 4,
                },
            }
            for i, (name, artist, album, tempo, energy, valence, dance, acoustic, inst, speech) in enumerate([
                ("Clair de Lune", "Debussy", "Suite Bergamasque", 72.0, 0.18, 0.42, 0.22, 0.91, 0.97, 0.03),
                ("Experience", "Ludovico Einaudi", "In a Time Lapse", 75.0, 0.25, 0.55, 0.28, 0.85, 0.92, 0.02),
                ("River Flows in You", "Yiruma", "First Love", 68.0, 0.15, 0.58, 0.20, 0.94, 0.98, 0.02),
                ("Nuvole Bianche", "Ludovico Einaudi", "Una Mattina", 65.0, 0.20, 0.50, 0.18, 0.88, 0.95, 0.02),
                ("Time", "Hans Zimmer", "Inception OST", 80.0, 0.35, 0.45, 0.30, 0.75, 0.94, 0.03),
                ("Weightless", "Marconi Union", "Weightless", 60.0, 0.12, 0.40, 0.15, 0.82, 0.96, 0.01),
                ("Gymnopédie No.1", "Erik Satie", "Gymnopédies", 58.0, 0.10, 0.52, 0.16, 0.95, 0.99, 0.02),
                ("November", "Max Richter", "The Blue Notebooks", 70.0, 0.22, 0.48, 0.25, 0.78, 0.93, 0.03),
                ("On the Nature of Daylight", "Max Richter", "The Blue Notebooks", 66.0, 0.18, 0.44, 0.20, 0.80, 0.95, 0.02),
                ("Comptine d'un autre été", "Yann Tiersen", "Amélie OST", 82.0, 0.28, 0.60, 0.32, 0.72, 0.89, 0.04),
                ("Spiegel im Spiegel", "Arvo Pärt", "Tabula Rasa", 55.0, 0.08, 0.46, 0.12, 0.90, 0.98, 0.01),
                ("A Whiter Shade of Pale", "Procol Harum", "Procol Harum", 76.0, 0.32, 0.54, 0.35, 0.62, 0.15, 0.08),
                ("Lo-Fi Study Beat #1", "ChillHop", "Study Beats Vol.1", 85.0, 0.38, 0.55, 0.45, 0.45, 0.72, 0.05),
                ("Forest Rain", "Ambient Works", "Nature Sounds", 50.0, 0.08, 0.62, 0.10, 0.96, 0.99, 0.00),
                ("Deep Focus", "Neural Mix", "Concentration Series", 88.0, 0.42, 0.48, 0.40, 0.30, 0.85, 0.04),
                ("Holocene", "Bon Iver", "Bon Iver", 90.0, 0.40, 0.58, 0.38, 0.55, 0.05, 0.06),
                ("The Night Will Always Win", "Manchester Orchestra", "Cope", 78.0, 0.45, 0.52, 0.42, 0.48, 0.02, 0.05),
                ("Slow Hours", "Jon Hopkins", "Immunity", 72.0, 0.30, 0.44, 0.35, 0.35, 0.75, 0.03),
                ("Glass", "Ólafur Arnalds", "And They Have Escaped", 68.0, 0.20, 0.50, 0.22, 0.70, 0.88, 0.02),
                ("Near Light", "Ólafur Arnalds", "Living Room Songs", 62.0, 0.15, 0.46, 0.18, 0.75, 0.90, 0.02),
            ])
        ]
        return mock_tracks


# Singleton instance
spotify_client = SpotifyClient()
