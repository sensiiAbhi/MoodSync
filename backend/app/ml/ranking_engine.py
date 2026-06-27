"""
MoodSync Ranking Engine
Scores and ranks candidate tracks against the target music profile.
Implements the 3-component scoring formula:
  Final Score = α × MAS + β × HES + γ × PPS
"""
from __future__ import annotations
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.ml.context_fusion import MusicProfile


@dataclass
class ScoredTrack:
    spotify_id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    preview_url: Optional[str]
    spotify_url: str
    album_art_url: Optional[str]

    # Audio Features
    tempo: float
    energy: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    speechiness: float

    # Scores
    mood_alignment_score: float
    historical_effectiveness_score: float
    personal_preference_score: float
    final_score: float

    rank: int
    explanation: str


class RankingEngine:
    """
    Ranks Spotify candidate tracks using a weighted 3-component scoring system.
    """

    DEFAULT_WEIGHTS = {"alpha": 0.45, "beta": 0.30, "gamma": 0.25}

    def rank_tracks(
        self,
        candidates: List[Dict[str, Any]],
        profile: MusicProfile,
        user_weights: Optional[Dict[str, float]] = None,
        historical_ratings: Optional[Dict[str, float]] = None,
        personal_history: Optional[Dict[str, float]] = None,
    ) -> List[ScoredTrack]:
        """
        Rank candidate tracks from Spotify against the target music profile.

        Args:
            candidates: List of track dicts with audio features from Spotify API
            profile: Target MusicProfile from context fusion
            user_weights: Custom alpha/beta/gamma weights per user
            historical_ratings: {spotify_id: avg_rating_0_to_1} from similar users
            personal_history: {spotify_id: preference_0_to_1} from user's own history

        Returns:
            Sorted list of ScoredTrack objects
        """
        weights = user_weights or self.DEFAULT_WEIGHTS
        alpha = weights.get("alpha", 0.45)
        beta = weights.get("beta", 0.30)
        gamma = weights.get("gamma", 0.25)

        scored = []
        for track in candidates:
            features = self._extract_features(track)
            if features is None:
                continue

            mas = self._compute_mas(features, profile)
            hes = (historical_ratings or {}).get(track.get("id", ""), 0.5)
            pps = (personal_history or {}).get(track.get("id", ""), 0.0)

            final = alpha * mas + beta * hes + gamma * pps
            explanation = self._build_explanation(features, profile, mas, hes, pps)

            scored.append(
                ScoredTrack(
                    spotify_id=track.get("id", ""),
                    title=track.get("name", "Unknown"),
                    artist=", ".join(
                        a["name"] for a in track.get("artists", [])
                    ),
                    album=track.get("album", {}).get("name", ""),
                    duration_ms=track.get("duration_ms", 0),
                    preview_url=track.get("preview_url"),
                    spotify_url=track.get("external_urls", {}).get("spotify", ""),
                    album_art_url=(
                        track.get("album", {}).get("images", [{}])[0].get("url")
                        if track.get("album", {}).get("images")
                        else None
                    ),
                    tempo=features.get("tempo", 0),
                    energy=features.get("energy", 0),
                    valence=features.get("valence", 0),
                    danceability=features.get("danceability", 0),
                    acousticness=features.get("acousticness", 0),
                    instrumentalness=features.get("instrumentalness", 0),
                    speechiness=features.get("speechiness", 0),
                    mood_alignment_score=round(mas, 4),
                    historical_effectiveness_score=round(hes, 4),
                    personal_preference_score=round(pps, 4),
                    final_score=round(final, 4),
                    rank=0,  # set after sorting
                    explanation=explanation,
                )
            )

        # Sort by final score descending
        scored.sort(key=lambda t: t.final_score, reverse=True)

        # Apply diversity filter (avoid too many same-artist consecutive tracks)
        scored = self._apply_diversity_filter(scored)

        # Assign ranks
        for i, track in enumerate(scored):
            track.rank = i + 1

        return scored[:25]  # Return top 25 tracks based on exact combinations

    def _extract_features(self, track: Dict) -> Optional[Dict[str, float]]:
        """Extract audio feature vector from Spotify track+features dict."""
        features = track.get("audio_features") or track
        required = ["tempo", "energy", "valence", "danceability",
                    "acousticness", "instrumentalness", "speechiness"]
        if not all(k in features for k in required):
            return None
        return {k: float(features[k]) for k in required}

    def _compute_mas(self, features: Dict[str, float], profile: MusicProfile) -> float:
        """
        Compute Mood Alignment Score via normalized Euclidean distance
        between track features and target profile center.
        Returns value in [0, 1] where 1 = perfect match.
        """
        # Feature vector: [tempo_norm, energy, valence, instrumentalness,
        #                  acousticness, danceability]
        tempo_norm = features["tempo"] / 200.0
        target_tempo_norm = profile.tempo_target / 200.0

        dims = [
            (tempo_norm, target_tempo_norm, 1.5),
            (features["energy"], profile.energy_target, 2.0),
            (features["valence"], profile.valence_target, 1.5),
            (features["instrumentalness"], profile.instrumentalness_target, 2.5),
            (features["acousticness"],
             (profile.acousticness_min + profile.acousticness_max) / 2, 1.0),
            (features["danceability"],
             (profile.danceability_min + profile.danceability_max) / 2, 0.5),
        ]

        total_weight = sum(w for _, _, w in dims)
        weighted_sq_dist = sum(
            w * (v - t) ** 2 for v, t, w in dims
        ) / total_weight

        # Convert distance to similarity: score = e^(-5 * dist)
        distance = math.sqrt(weighted_sq_dist)
        score = math.exp(-4.0 * distance)
        return min(1.0, score)

    def _build_explanation(
        self,
        features: Dict[str, float],
        profile: MusicProfile,
        mas: float,
        hes: float,
        pps: float,
    ) -> str:
        parts = []

        if features["instrumentalness"] >= 0.70:
            parts.append("highly instrumental — minimal vocal distraction")
        elif features["instrumentalness"] >= 0.40:
            parts.append("mostly instrumental with some vocals")

        tempo = features["tempo"]
        if tempo < 72:
            parts.append(f"slow tempo ({tempo:.0f} BPM) for calm focus")
        elif tempo < 100:
            parts.append(f"moderate tempo ({tempo:.0f} BPM) for balanced energy")
        else:
            parts.append(f"upbeat tempo ({tempo:.0f} BPM) for high energy")

        energy = features["energy"]
        if energy < 0.35:
            parts.append("low energy — perfect for relaxed concentration")
        elif energy < 0.65:
            parts.append("moderate energy — balanced and engaging")
        else:
            parts.append("high energy — energizing and motivating")

        if mas >= 0.80:
            parts.append(f"{int(mas*100)}% mood alignment score")
        elif mas >= 0.60:
            parts.append(f"{int(mas*100)}% mood alignment score — good match")

        return "; ".join(parts).capitalize() + "."

    def _apply_diversity_filter(self, tracks: List[ScoredTrack]) -> List[ScoredTrack]:
        """Prevent more than 2 consecutive tracks by the same artist."""
        result = []
        artist_consecutive: Dict[str, int] = {}
        deferred = []

        for track in tracks:
            artist = track.artist
            count = artist_consecutive.get(artist, 0)
            if count < 2:
                result.append(track)
                artist_consecutive[artist] = count + 1
            else:
                deferred.append(track)

        # Append deferred tracks at end
        result.extend(deferred)
        return result


# Singleton instance
ranking_engine = RankingEngine()
