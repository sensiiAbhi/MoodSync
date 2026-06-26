"""
MoodSync Context Fusion Engine
Combines mood classification + activity + desired outcome
to produce a target Music Feature Profile using the ISO Principle.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class MusicProfile:
    """Target audio feature profile for Spotify recommendation query."""
    # Tempo
    tempo_min: float
    tempo_max: float
    tempo_target: float

    # Energy
    energy_min: float
    energy_max: float
    energy_target: float

    # Valence (musical positivity)
    valence_min: float
    valence_max: float
    valence_target: float

    # Instrumentalness (0=vocal, 1=instrumental)
    instrumentalness_min: float
    instrumentalness_target: float

    # Acousticness
    acousticness_min: float
    acousticness_max: float

    # Danceability
    danceability_min: float
    danceability_max: float

    # Speechiness
    speechiness_max: float

    # Seed Genres
    seed_genres: List[str]

    # Human-readable context summary
    profile_rationale: str = ""


# ─────────────────────────────────────────────────────────────────
# BASE MOOD PROFILES (ISO Principle: match current state then guide)
# ─────────────────────────────────────────────────────────────────
MOOD_BASE_PROFILES = {
    "stressed": MusicProfile(
        tempo_min=55, tempo_max=85, tempo_target=70,
        energy_min=0.20, energy_max=0.45, energy_target=0.35,
        valence_min=0.35, valence_max=0.65, valence_target=0.50,
        instrumentalness_min=0.60, instrumentalness_target=0.80,
        acousticness_min=0.45, acousticness_max=0.90,
        danceability_min=0.15, danceability_max=0.45,
        speechiness_max=0.07,
        seed_genres=["classical", "ambient", "piano", "new-age"],
    ),
    "anxious": MusicProfile(
        tempo_min=50, tempo_max=78, tempo_target=65,
        energy_min=0.15, energy_max=0.40, energy_target=0.28,
        valence_min=0.30, valence_max=0.60, valence_target=0.48,
        instrumentalness_min=0.65, instrumentalness_target=0.85,
        acousticness_min=0.55, acousticness_max=1.0,
        danceability_min=0.10, danceability_max=0.40,
        speechiness_max=0.05,
        seed_genres=["ambient", "new-age", "sleep", "classical"],
    ),
    "burned_out": MusicProfile(
        tempo_min=55, tempo_max=88, tempo_target=72,
        energy_min=0.18, energy_max=0.42, energy_target=0.30,
        valence_min=0.40, valence_max=0.70, valence_target=0.55,
        instrumentalness_min=0.50, instrumentalness_target=0.70,
        acousticness_min=0.40, acousticness_max=0.85,
        danceability_min=0.20, danceability_max=0.50,
        speechiness_max=0.10,
        seed_genres=["jazz", "acoustic", "indie", "soul"],
    ),
    "sleepy": MusicProfile(
        tempo_min=45, tempo_max=72, tempo_target=60,
        energy_min=0.05, energy_max=0.28, energy_target=0.15,
        valence_min=0.35, valence_max=0.65, valence_target=0.50,
        instrumentalness_min=0.70, instrumentalness_target=0.92,
        acousticness_min=0.65, acousticness_max=1.0,
        danceability_min=0.05, danceability_max=0.30,
        speechiness_max=0.03,
        seed_genres=["sleep", "ambient", "classical", "acoustic"],
    ),
    "energetic": MusicProfile(
        tempo_min=110, tempo_max=160, tempo_target=135,
        energy_min=0.65, energy_max=0.95, energy_target=0.80,
        valence_min=0.60, valence_max=0.95, valence_target=0.78,
        instrumentalness_min=0.00, instrumentalness_target=0.15,
        acousticness_min=0.00, acousticness_max=0.40,
        danceability_min=0.55, danceability_max=0.95,
        speechiness_max=0.25,
        seed_genres=["hip-hop", "rock", "electronic", "pop"],
    ),
    "motivated": MusicProfile(
        tempo_min=100, tempo_max=150, tempo_target=128,
        energy_min=0.65, energy_max=0.92, energy_target=0.78,
        valence_min=0.65, valence_max=0.95, valence_target=0.80,
        instrumentalness_min=0.00, instrumentalness_target=0.20,
        acousticness_min=0.00, acousticness_max=0.35,
        danceability_min=0.50, danceability_max=0.90,
        speechiness_max=0.20,
        seed_genres=["power-pop", "electronic", "rock", "hip-hop"],
    ),
    "calm": MusicProfile(
        tempo_min=60, tempo_max=92, tempo_target=75,
        energy_min=0.18, energy_max=0.45, energy_target=0.32,
        valence_min=0.45, valence_max=0.78, valence_target=0.62,
        instrumentalness_min=0.45, instrumentalness_target=0.65,
        acousticness_min=0.50, acousticness_max=0.90,
        danceability_min=0.20, danceability_max=0.55,
        speechiness_max=0.10,
        seed_genres=["acoustic", "folk", "indie", "jazz"],
    ),
    "focused": MusicProfile(
        tempo_min=68, tempo_max=95, tempo_target=82,
        energy_min=0.30, energy_max=0.60, energy_target=0.45,
        valence_min=0.38, valence_max=0.65, valence_target=0.52,
        instrumentalness_min=0.75, instrumentalness_target=0.90,
        acousticness_min=0.30, acousticness_max=0.72,
        danceability_min=0.15, danceability_max=0.48,
        speechiness_max=0.05,
        seed_genres=["classical", "lo-fi", "post-rock", "neo-classical"],
    ),
    "relaxed": MusicProfile(
        tempo_min=58, tempo_max=88, tempo_target=73,
        energy_min=0.12, energy_max=0.42, energy_target=0.27,
        valence_min=0.52, valence_max=0.82, valence_target=0.67,
        instrumentalness_min=0.45, instrumentalness_target=0.60,
        acousticness_min=0.50, acousticness_max=0.92,
        danceability_min=0.20, danceability_max=0.55,
        speechiness_max=0.10,
        seed_genres=["jazz", "acoustic", "indie-pop", "soft-rock"],
    ),
}


# ─────────────────────────────────────────────────────────────────
# ACTIVITY MODIFIERS
# ─────────────────────────────────────────────────────────────────
ACTIVITY_MODIFIERS = {
    "studying": {
        "tempo_delta": -10,
        "energy_delta": -0.08,
        "instrumentalness_min_override": 0.70,
        "speechiness_max_override": 0.05,
        "extra_genres": ["lo-fi", "study"],
    },
    "coding": {
        "tempo_delta": 0,
        "energy_delta": +0.05,
        "instrumentalness_min_override": 0.65,
        "speechiness_max_override": 0.06,
        "extra_genres": ["electronic", "synth"],
    },
    "reading": {
        "tempo_delta": -15,
        "energy_delta": -0.12,
        "instrumentalness_min_override": 0.75,
        "speechiness_max_override": 0.04,
        "extra_genres": ["acoustic", "chamber-music"],
    },
    "deep_work": {
        "tempo_delta": -10,
        "energy_delta": -0.05,
        "instrumentalness_min_override": 0.80,
        "speechiness_max_override": 0.03,
        "extra_genres": ["classical", "neo-classical"],
    },
    "creative_thinking": {
        "tempo_delta": +5,
        "energy_delta": +0.08,
        "instrumentalness_min_override": 0.35,
        "speechiness_max_override": 0.12,
        "extra_genres": ["indie", "experimental"],
    },
    "gym_workout": {
        "tempo_delta": +25,
        "energy_delta": +0.25,
        "instrumentalness_min_override": 0.00,
        "speechiness_max_override": 0.25,
        "extra_genres": ["hip-hop", "electronic", "metal"],
    },
    "running": {
        "tempo_delta": +18,
        "energy_delta": +0.20,
        "instrumentalness_min_override": 0.00,
        "speechiness_max_override": 0.22,
        "extra_genres": ["pop", "electronic"],
    },
    "yoga": {
        "tempo_delta": -18,
        "energy_delta": -0.22,
        "instrumentalness_min_override": 0.65,
        "speechiness_max_override": 0.06,
        "extra_genres": ["ambient", "new-age", "world-music"],
    },
    "meditation": {
        "tempo_delta": -22,
        "energy_delta": -0.28,
        "instrumentalness_min_override": 0.88,
        "speechiness_max_override": 0.02,
        "extra_genres": ["ambient", "drone", "new-age"],
    },
    "sleeping": {
        "tempo_delta": -22,
        "energy_delta": -0.30,
        "instrumentalness_min_override": 0.90,
        "speechiness_max_override": 0.01,
        "extra_genres": ["sleep", "ambient"],
    },
    "relaxing": {
        "tempo_delta": -10,
        "energy_delta": -0.12,
        "instrumentalness_min_override": 0.50,
        "speechiness_max_override": 0.10,
        "extra_genres": ["jazz", "acoustic"],
    },
    "driving": {
        "tempo_delta": +12,
        "energy_delta": +0.10,
        "instrumentalness_min_override": 0.10,
        "speechiness_max_override": 0.18,
        "extra_genres": ["pop", "indie-pop", "rock"],
    },
    "working": {
        "tempo_delta": 0,
        "energy_delta": +0.05,
        "instrumentalness_min_override": 0.55,
        "speechiness_max_override": 0.08,
        "extra_genres": ["classical", "jazz", "lo-fi"],
    },
}


class ContextFusionEngine:
    """
    Combines mood classification with activity and desired outcome
    to produce a MusicProfile for Spotify recommendation queries.
    Applies the ISO Principle: match current state, guide toward goal.
    """

    def build_music_profile(
        self,
        primary_mood: str,
        activity_type: str,
        desired_outcome: str | None = None,
    ) -> MusicProfile:
        """
        Build a MusicProfile from mood + activity context.
        Returns a cloned, activity-adjusted profile.
        """
        mood_key = primary_mood.lower().replace(" ", "_")
        activity_key = activity_type.lower().replace(" ", "_")

        # Get base mood profile (default to 'calm' if unknown)
        base = MOOD_BASE_PROFILES.get(mood_key, MOOD_BASE_PROFILES["calm"])
        modifier = ACTIVITY_MODIFIERS.get(activity_key, {})

        # Build adjusted profile
        tempo_delta = modifier.get("tempo_delta", 0)
        energy_delta = modifier.get("energy_delta", 0.0)
        inst_min_override = modifier.get("instrumentalness_min_override")
        speech_max_override = modifier.get("speechiness_max_override")
        extra_genres = modifier.get("extra_genres", [])

        # Clamp values to valid Spotify ranges
        def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
            return max(lo, min(hi, val))

        adjusted = MusicProfile(
            tempo_min=max(40, base.tempo_min + tempo_delta),
            tempo_max=min(200, base.tempo_max + tempo_delta),
            tempo_target=max(40, min(200, base.tempo_target + tempo_delta)),

            energy_min=clamp(base.energy_min + energy_delta),
            energy_max=clamp(base.energy_max + energy_delta),
            energy_target=clamp(base.energy_target + energy_delta),

            valence_min=base.valence_min,
            valence_max=base.valence_max,
            valence_target=base.valence_target,

            instrumentalness_min=(
                inst_min_override
                if inst_min_override is not None
                else base.instrumentalness_min
            ),
            instrumentalness_target=max(
                inst_min_override or base.instrumentalness_min,
                base.instrumentalness_target,
            ),

            acousticness_min=base.acousticness_min,
            acousticness_max=base.acousticness_max,

            danceability_min=base.danceability_min,
            danceability_max=base.danceability_max,

            speechiness_max=(
                speech_max_override
                if speech_max_override is not None
                else base.speechiness_max
            ),

            seed_genres=list(dict.fromkeys(base.seed_genres + extra_genres))[:5],

            profile_rationale=self._build_rationale(
                mood_key, activity_key, desired_outcome
            ),
        )

        return adjusted

    def _build_rationale(
        self,
        mood: str,
        activity: str,
        outcome: str | None,
    ) -> str:
        mood_label = mood.replace("_", " ").title()
        activity_label = activity.replace("_", " ").title()
        outcome_label = (outcome or "").replace("_", " ").title()
        return (
            f"Matched for a {mood_label} person doing {activity_label}"
            + (f" aiming to {outcome_label}" if outcome_label else "")
            + ". Using ISO Principle: music gradually guides your mood toward the desired state."
        )

    def profile_to_spotify_params(self, profile: MusicProfile) -> dict:
        """Convert MusicProfile to Spotify API recommendation parameters."""
        params = {
            "target_tempo": profile.tempo_target,
            "min_tempo": profile.tempo_min,
            "max_tempo": profile.tempo_max,
            "target_energy": profile.energy_target,
            "min_energy": profile.energy_min,
            "max_energy": profile.energy_max,
            "target_valence": profile.valence_target,
            "min_valence": profile.valence_min,
            "max_valence": profile.valence_max,
            "target_instrumentalness": profile.instrumentalness_target,
            "min_instrumentalness": profile.instrumentalness_min,
            "target_acousticness": (profile.acousticness_min + profile.acousticness_max) / 2,
            "min_acousticness": profile.acousticness_min,
            "max_acousticness": profile.acousticness_max,
            "target_danceability": (profile.danceability_min + profile.danceability_max) / 2,
            "min_danceability": profile.danceability_min,
            "max_danceability": profile.danceability_max,
            "max_speechiness": profile.speechiness_max,
            "seed_genres": ",".join(profile.seed_genres[:5]),
            "limit": 50,
        }
        return params


# Singleton instance
context_fusion_engine = ContextFusionEngine()
